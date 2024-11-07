# server/api/services/stock_service.py
from typing import Optional, Dict, List
from decimal import Decimal
from .stock_providers.base_provider import StockDataProvider
import logging
import asyncio

class StockService:
    """Service for fetching stock data from configured provider"""
    
    def __init__(self, provider: StockDataProvider):
        self.provider = provider
        self.logger = logging.getLogger(__name__)
        
    async def get_stock_info(self, symbol: str) -> Dict:
        """Get detailed stock information"""
        try:
            return await self.provider.get_stock_info(symbol)
        except Exception as e:
            self.logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            raise
        
    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, Decimal]:
        """Get current prices for multiple symbols"""
        try:
            return await self.provider.get_batch_quotes(symbols)
        except Exception as e:
            self.logger.error(f"Error getting batch quotes: {str(e)}")
            raise
        
    async def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by symbol or name"""
        try:
            return await self.provider.search_stocks(query)
        except Exception as e:
            self.logger.error(f"Error searching stocks: {str(e)}")
            raise
        
    async def get_market_status(self) -> Dict:
        """Get current market status"""
        try:
            return await self.provider.get_market_status()
        except Exception as e:
            self.logger.error(f"Error getting market status: {str(e)}")
            raise