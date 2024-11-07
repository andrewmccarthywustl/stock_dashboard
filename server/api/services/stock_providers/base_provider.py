# server/api/services/stock_providers/base_provider.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from decimal import Decimal

class StockDataProvider(ABC):
    """Abstract base class for stock data providers"""
    
    @abstractmethod
    async def get_stock_info(self, symbol: str) -> Dict:
        """Get detailed stock information"""
        pass
        
    @abstractmethod
    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, Decimal]:
        """Get current prices for multiple symbols"""
        pass
        
    @abstractmethod
    async def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by symbol or name"""
        pass
        
    @abstractmethod
    async def get_market_status(self) -> Dict:
        """Get current market status"""
        pass
        
    @abstractmethod
    async def cleanup(self):
        """Clean up any resources"""
        pass