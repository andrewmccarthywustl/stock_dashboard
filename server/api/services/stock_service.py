# server/api/services/stock_service.py
import aiohttp
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging
from functools import lru_cache
import time
import ssl
from ..config import Config

logger = logging.getLogger(__name__)

class StockServiceError(Exception):
    """Base exception for stock service errors"""
    pass

class RateLimitError(StockServiceError):
    """Raised when API rate limit is exceeded"""
    pass

class APIError(StockServiceError):
    """Raised when API returns an error"""
    pass

class StockService:
    """Service for fetching stock data from external APIs"""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    CACHE_TTL = 300  # Cache TTL in seconds (5 minutes)
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the stock service
        
        Args:
            api_key: Optional API key (will use config if not provided)
        """
        self.api_key = api_key or Config.FMP_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit = asyncio.Semaphore(30)  # Limit concurrent requests
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum time between requests in seconds
        self.logger = logging.getLogger(__name__)
        
        # Create SSL context that ignores verification (development only)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def __aenter__(self):
        """Setup async context"""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async context"""
        await self.cleanup()

    async def setup(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_context)
            )

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None

    def _respect_rate_limit(self):
        """Ensure minimum time between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting and error handling
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            StockServiceError: If request fails
        """
        if not self.session:
            await self.setup()

        params = params or {}
        params['apikey'] = self.api_key

        async with self.rate_limit:
            self._respect_rate_limit()
            try:
                async with self.session.get(
                    f"{self.BASE_URL}/{endpoint}",
                    params=params,
                    ssl=self.ssl_context,
                    timeout=10
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("API rate limit exceeded")
                    
                    if response.status != 200:
                        raise APIError(f"API request failed: {response.status}")
                    
                    data = await response.json()
                    
                    if not data:
                        return self._get_mock_stock_info(params.get('symbol', 'UNKNOWN'))
                    
                    return data
                    
            except aiohttp.ClientError as e:
                self.logger.error(f"Request failed: {str(e)}")
                raise StockServiceError(f"Request failed: {str(e)}")
            except asyncio.TimeoutError:
                self.logger.error("Request timed out")
                raise StockServiceError("Request timed out")
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                raise StockServiceError(f"Unexpected error: {str(e)}")

    def _get_mock_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Provide mock stock data for development
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Mock stock data
        """
        mock_sectors = {
            'A': 'Technology',
            'B': 'Healthcare',
            'C': 'Finance',
            'D': 'Consumer Goods',
            'E': 'Industrial'
        }
        
        mock_industries = {
            'Technology': 'Software',
            'Healthcare': 'Biotechnology',
            'Finance': 'Banking',
            'Consumer Goods': 'Retail',
            'Industrial': 'Manufacturing'
        }
        
        first_letter = symbol[0].upper()
        sector = mock_sectors.get(first_letter, 'Technology')
        
        return {
            "symbol": symbol,
            "name": f"{symbol} Inc.",
            "sector": sector,
            "industry": mock_industries.get(sector, 'Software'),
            "price": Decimal("100.00"),
            "beta": 1.0,
            "market_cap": Decimal("1000000000"),
            "exchange": "NYSE",
            "currency": "USD",
            "last_updated": datetime.now().isoformat()
        }

    @lru_cache(maxsize=1000)
    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get stock information with caching and fallback
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Stock information
        """
        try:
            data = await self._make_request(f"profile/{symbol}")
            
            if not data or not isinstance(data, list):
                return self._get_mock_stock_info(symbol)
            
            stock_info = data[0]
            
            return {
                "symbol": stock_info.get('symbol'),
                "name": stock_info.get('companyName'),
                "sector": stock_info.get('sector', 'Technology'),
                "industry": stock_info.get('industry', 'Software'),
                "price": Decimal(str(stock_info.get('price', '100.00'))),
                "beta": float(stock_info.get('beta', '1.0')),
                "market_cap": Decimal(str(stock_info.get('mktCap', '1000000000'))),
                "exchange": stock_info.get('exchange', 'NYSE'),
                "currency": stock_info.get('currency', 'USD'),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get real stock data for {symbol}: {str(e)}, using mock data")
            return self._get_mock_stock_info(symbol)

    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, Decimal]:
        """Get current prices for multiple stocks with fallback
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary of symbols and their prices
        """
        if not symbols:
            return {}
            
        try:
            symbols_str = ','.join(symbols)
            data = await self._make_request(f"quote/{symbols_str}")
            
            quotes = {}
            for quote in data:
                if 'symbol' in quote and 'price' in quote:
                    try:
                        quotes[quote['symbol']] = Decimal(str(quote['price']))
                    except (TypeError, ValueError):
                        quotes[quote['symbol']] = Decimal('100.00')
            
            # Add mock data for any missing symbols
            for symbol in symbols:
                if symbol not in quotes:
                    quotes[symbol] = Decimal('100.00')
                    
            return quotes
            
        except Exception as e:
            self.logger.warning(f"Failed to get batch quotes: {str(e)}, using mock data")
            return {symbol: Decimal("100.00") for symbol in symbols}

    async def get_market_status(self) -> Dict[str, Any]:
        """Get current market status with fallback
        
        Returns:
            Market status information
        """
        try:
            data = await self._make_request("market-status")
            
            return {
                "market_status": data[0].get('market_status', 'open'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get market status: {str(e)}, using mock data")
            return {
                "market_status": "open",
                "timestamp": datetime.now().isoformat()
            }

    async def search_stocks(self, query: str) -> List[Dict[str, str]]:
        """Search for stocks by symbol or name with fallback
        
        Args:
            query: Search query
            
        Returns:
            List of matching stocks
        """
        try:
            data = await self._make_request("search", {"query": query})
            
            return [{
                "symbol": item.get('symbol'),
                "name": item.get('name'),
                "exchange": item.get('exchange'),
                "type": item.get('type')
            } for item in data]
            
        except Exception as e:
            self.logger.warning(f"Failed to search stocks: {str(e)}, using mock data")
            return [{
                "symbol": query.upper(),
                "name": f"{query.upper()} Inc.",
                "exchange": "NYSE",
                "type": "stock"
            }]

    def invalidate_cache(self, symbol: Optional[str] = None):
        """Invalidate cache for a specific symbol or all symbols
        
        Args:
            symbol: Optional symbol to invalidate
        """
        if symbol:
            self.get_stock_info.cache_clear()
        else:
            # Clear all caches
            self.get_stock_info.cache_clear()