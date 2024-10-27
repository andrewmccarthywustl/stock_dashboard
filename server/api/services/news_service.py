import requests
from typing import Dict, List, Any
from config.settings import Config
from utils.api_helpers import retry_on_failure, APIError

class NewsService:
    @staticmethod
    @retry_on_failure(max_retries=3)
    def get_stock_news(symbol: str) -> List[Dict[str, Any]]:
        """Get news articles for a stock symbol"""
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "apikey": Config.ALPHA_VANTAGE_API_KEY,
        }
        
        try:
            response = requests.get(
                url="https://www.alphavantage.co/query",
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "feed" not in data:
                raise APIError(f"No news data found for symbol: {symbol}")
                
            return data["feed"]
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch news: {str(e)}")