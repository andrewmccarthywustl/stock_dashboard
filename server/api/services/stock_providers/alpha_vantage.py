# server/api/services/stock_providers/alpha_vantage.py
from decimal import Decimal
from typing import Dict, List, Optional, Any
import aiohttp
import logging
from datetime import datetime, timedelta
import asyncio
from .base_provider import StockDataProvider
import ssl
import certifi
import os

logger = logging.getLogger(__name__)

class AlphaVantageProvider(StockDataProvider):
    """Alpha Vantage implementation of stock data provider with premium features"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    BATCH_SIZE = 100  # Maximum symbols per batch request for premium tier
    
    def __init__(self, api_key: str):
        """Initialize provider with API key and configure client session"""
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
        self._last_request_time = datetime.now()
        self._request_count = 0
        self._reset_time = datetime.now()
        
        # Certificate handling
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Cache for company information
        self._company_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self.CACHE_DURATION = timedelta(hours=24)  # Cache company info for 24 hours

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists and is active"""
        if self.session is None or self.session.closed:
            conn = aiohttp.TCPConnector(
                ssl=self.ssl_context,
                force_close=False,
                enable_cleanup_closed=True,
                verify_ssl=True
            )
            self.session = aiohttp.ClientSession(connector=conn)

    async def _make_request(self, params: Dict) -> Dict:
        """Make API request with error handling and rate limiting"""
        await self._ensure_session()
        
        params['apikey'] = self.api_key
        
        async with self._request_semaphore:
            try:
                # Add timeout for the request
                timeout = aiohttp.ClientTimeout(total=30)
                
                async with self.session.get(
                    self.BASE_URL, 
                    params=params,
                    timeout=timeout,
                    ssl=self.ssl_context
                ) as response:
                    if response.status == 429:
                        logger.warning("Rate limit exceeded, waiting to retry")
                        await asyncio.sleep(60)
                        return await self._make_request(params)
                    
                    # Ensure successful response
                    response.raise_for_status()
                    
                    data = await response.json()
                    
                    if "Error Message" in data:
                        raise ValueError(data["Error Message"])
                        
                    if "Note" in data and "API call frequency" in data["Note"]:
                        logger.warning("API frequency warning received")
                        await asyncio.sleep(60)
                        
                    return data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Network error in Alpha Vantage request: {str(e)}")
                raise
            except ValueError as e:
                logger.error(f"Invalid data received from Alpha Vantage: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Alpha Vantage request: {str(e)}")
                raise

    async def get_company_info(self, symbol: str) -> Dict:
        """Get company overview data with caching"""
        # Check cache first
        if (symbol in self._company_cache and 
            symbol in self._cache_expiry and 
            datetime.now() < self._cache_expiry[symbol]):
            return self._company_cache[symbol]

        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        try:
            data = await self._make_request(params)
            
            company_info = {
                'name': data.get('Name', 'Unknown'),
                'sector': data.get('Sector', 'Unknown'),
                'industry': data.get('Industry', 'Unknown'),
                'beta': float(data.get('Beta', '1.0'))
            }
            
            # Cache the results
            self._company_cache[symbol] = company_info
            self._cache_expiry[symbol] = datetime.now() + self.CACHE_DURATION
            
            return company_info
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return {
                'name': 'Unknown',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'beta': 1.0
            }

    async def get_stock_info(self, symbol: str) -> Dict:
        """Get detailed stock information including price and company data"""
        # Get company info and current price in parallel
        company_info_task = self.get_company_info(symbol)
        quote_params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        try:
            quote_task = self._make_request(quote_params)
            company_info, quote_data = await asyncio.gather(
                company_info_task,
                quote_task
            )
            
            price = Decimal(str(quote_data.get('Global Quote', {}).get('05. price', '0')))
            
            return {
                'symbol': symbol,
                'name': company_info['name'],
                'sector': company_info['sector'],
                'industry': company_info['industry'],
                'beta': company_info['beta'],
                'price': price,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing stock info for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'name': 'Unknown',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'beta': 1.0,
                'price': Decimal('0'),
                'last_updated': datetime.now().isoformat()
            }

    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, Decimal]:
        """Get quotes for multiple symbols using premium bulk quote endpoint"""
        if not symbols:
            return {}
            
        quotes = {}
        
        try:
            # Split symbols into batches of BATCH_SIZE
            for i in range(0, len(symbols), self.BATCH_SIZE):
                batch = symbols[i:i + self.BATCH_SIZE]
                params = {
                    'function': 'REALTIME_BULK_QUOTES',
                    'symbols': ','.join(batch)
                }
                
                response = await self._make_request(params)
                
                # Process batch quotes response
                if 'Stock Quotes' in response:
                    for quote in response['Stock Quotes']:
                        try:
                            symbol = quote.get('1. symbol', '')
                            price = quote.get('2. price', '0')
                            quotes[symbol] = Decimal(str(price))
                        except (TypeError, ValueError) as e:
                            logger.error(f"Error parsing price for {symbol}: {e}")
                            continue
                            
            return quotes
            
        except Exception as e:
            logger.error(f"Error in batch quotes: {str(e)}")
            return {}

    async def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by symbol or name"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': query
        }
        
        try:
            data = await self._make_request(params)
            results = []
            
            for match in data.get('bestMatches', []):
                results.append({
                    'symbol': match.get('1. symbol'),
                    'name': match.get('2. name'),
                    'type': match.get('3. type'),
                    'region': match.get('4. region'),
                    'currency': match.get('8. currency', 'USD')
                })
            return results
        except Exception as e:
            logger.error(f"Error searching stocks: {str(e)}")
            return []

    async def get_market_status(self) -> Dict:
        """Get market status using S&P 500 ETF (SPY) as proxy"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': 'SPY'
        }
        
        try:
            data = await self._make_request(params)
            quote_data = data.get('Global Quote', {})
            
            # If we can get a quote, market is likely open
            is_open = bool(quote_data.get('05. price'))
            
            return {
                'is_open': is_open,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting market status: {str(e)}")
            return {
                'is_open': False,
                'timestamp': datetime.now().isoformat()
            }

    async def cleanup(self):
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()