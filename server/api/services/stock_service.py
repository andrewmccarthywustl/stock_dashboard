import requests
from datetime import datetime
from typing import Dict, Any
from config.settings import Config
from utils.api_helpers import retry_on_failure, APIError

class StockService:
    BASE_URL = "https://financialmodelingprep.com/api/v3"

    @staticmethod
    @retry_on_failure(max_retries=3)
    def get_stock_info(symbol: str) -> Dict[str, Any]:
        """Get stock information with retry logic and error handling"""
        if not isinstance(symbol, str):
            raise ValueError("Symbol must be a string")
            
        symbol = symbol.upper().strip()
        if not symbol:
            raise ValueError("Symbol cannot be empty")
            
        try:
            response = requests.get(
                url=f"{StockService.BASE_URL}/profile/{symbol}",
                params={"apikey": Config.FMP_API_KEY},
                timeout=10
            )
            
            if response.status_code == 429:  # Rate limit
                raise APIError("Rate limit exceeded. Please try again later.")
                
            response.raise_for_status()
            
            stock_data = response.json()
            if not stock_data or len(stock_data) == 0:
                raise APIError(f"No data found for symbol: {symbol}")
            
            stock_info = stock_data[0]
            return {
                "symbol": stock_info.get('symbol'),
                "sector": stock_info.get('sector', 'Unknown'),
                "industry": stock_info.get('industry', 'Unknown'),
                "price": float(stock_info.get('price', 0)),
                "beta": float(stock_info.get('beta', 0)),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch data: {str(e)}")
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid data received from API: {str(e)}")

    @staticmethod
    @retry_on_failure(max_retries=3)
    def get_batch_quotes(symbols: list[str]) -> Dict[str, float]:
        """Get current prices for multiple stocks"""
        if not symbols:
            return {}
            
        try:
            symbols_str = ','.join(symbols)
            response = requests.get(
                url=f"{StockService.BASE_URL}/quote/{symbols_str}",
                params={"apikey": Config.FMP_API_KEY},
                timeout=10
            )
            
            response.raise_for_status()
            quotes = response.json()
            
            return {
                quote['symbol']: float(quote['price'])
                for quote in quotes
                if 'symbol' in quote and 'price' in quote
            }
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch batch quotes: {str(e)}")