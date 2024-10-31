# server/api/models/portfolio.py
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
import logging
from uuid import uuid4
from .base_model import BaseModel
from .position import Position
from .transaction import Transaction

logger = logging.getLogger(__name__)

class Portfolio(BaseModel):
    """Represents a portfolio with positions and transactions"""
    
    def __init__(
        self,
        portfolio_id: Optional[str] = None,
        positions: Optional[List[Position]] = None,
        transactions: Optional[List[Transaction]] = None,
        metadata: Optional[Dict] = None
    ):
        """Initialize portfolio with positions, transactions, and metadata
        
        Args:
            portfolio_id: Portfolio identifier
            positions: List of positions
            transactions: List of transactions
            metadata: Portfolio metadata
            
        Raises:
            ValueError: If inputs are invalid
        """
        try:
            # Initialize ID first for repository compatibility
            self._id = portfolio_id or f"PORT_{str(uuid4())[:8]}"
            
            # Validate inputs
            if positions is not None and not isinstance(positions, list):
                raise ValueError("Positions must be a list")
            if transactions is not None and not isinstance(transactions, list):
                raise ValueError("Transactions must be a list")
            
            self.positions = positions or []
            self.transactions = transactions or []
            self.last_updated = datetime.now()
            
            # Initialize metadata with defaults if not provided
            self.metadata = metadata or {
                "total_long_value": "0",
                "total_short_value": "0",
                "long_short_ratio": "N/A",
                "total_realized_gains": "0",
                "last_updated": self.last_updated.isoformat(),
                "sector_exposure": {
                    "long": {},
                    "short": {}
                },
                "long_positions_count": 0,
                "short_positions_count": 0,
                "weighted_long_beta": "0",
                "weighted_short_beta": "0"
            }
            
            # Validate all positions are Position objects
            if not all(isinstance(p, Position) for p in self.positions):
                raise ValueError("All positions must be Position objects")
                
            # Validate all transactions are Transaction objects
            if not all(isinstance(t, Transaction) for t in self.transactions):
                raise ValueError("All transactions must be Transaction objects")
                
        except Exception as e:
            logger.error(f"Error initializing portfolio: {str(e)}")
            raise

    @property
    def id(self) -> str:
        """Get portfolio ID for repository compatibility
        
        Returns:
            Portfolio identifier
        """
        return self._id
    
    @property
    def total_long_value(self) -> Decimal:
        """Calculate total value of long positions
        
        Returns:
            Total value of long positions
        """
        try:
            return sum(
                p.position_value 
                for p in self.positions 
                if p.position_type == 'long'
            ) or Decimal('0')
        except Exception as e:
            logger.error(f"Error calculating total long value: {str(e)}")
            return Decimal('0')
    
    @property
    def total_short_value(self) -> Decimal:
        """Calculate total value of short positions
        
        Returns:
            Total value of short positions
        """
        try:
            return sum(
                p.position_value 
                for p in self.positions 
                if p.position_type == 'short'
            ) or Decimal('0')
        except Exception as e:
            logger.error(f"Error calculating total short value: {str(e)}")
            return Decimal('0')
    
    @property
    def long_short_ratio(self) -> float:
        """Calculate long/short ratio
        
        Returns:
            Long/short ratio or float('inf') if no short positions
        """
        try:
            if self.total_short_value == 0:
                return float('inf')
            return float(self.total_long_value / self.total_short_value)
        except Exception as e:
            logger.error(f"Error calculating long/short ratio: {str(e)}")
            return float('inf')
    
    @property
    def total_realized_gains(self) -> Decimal:
        """Calculate total realized gains/losses
        
        Returns:
            Total realized gains/losses
        """
        try:
            return sum(
                (t.realized_gain or Decimal('0'))
                for t in self.transactions
            )
        except Exception as e:
            logger.error(f"Error calculating total realized gains: {str(e)}")
            return Decimal('0')
    
    @property
    def sector_exposure(self) -> Dict[str, Dict[str, float]]:
        """Calculate sector exposure for long and short positions
        
        Returns:
            Dictionary containing sector exposures for long and short positions
        """
        try:
            exposure = {'long': {}, 'short': {}}
            
            for position_type in ['long', 'short']:
                positions = [p for p in self.positions if p.position_type == position_type]
                total_value = sum(p.position_value for p in positions) or Decimal('0')
                
                if total_value > 0:
                    sector_values = {}
                    for position in positions:
                        sector_values[position.sector] = sector_values.get(
                            position.sector, Decimal('0')
                        ) + position.position_value
                    
                    exposure[position_type] = {
                        sector: float(value / total_value * 100)
                        for sector, value in sector_values.items()
                    }
                    
            return exposure
        except Exception as e:
            logger.error(f"Error calculating sector exposure: {str(e)}")
            return {'long': {}, 'short': {}}
    
    def update_metadata(self) -> None:
        """Update portfolio metadata"""
        try:
            self.metadata.update({
                "total_long_value": str(self.total_long_value),
                "total_short_value": str(self.total_short_value),
                "long_short_ratio": str(self.long_short_ratio),
                "total_realized_gains": str(self.total_realized_gains),
                "last_updated": datetime.now().isoformat(),
                "sector_exposure": self.sector_exposure,
                "long_positions_count": len([p for p in self.positions if p.position_type == "long"]),
                "short_positions_count": len([p for p in self.positions if p.position_type == "short"])
            })
            self.last_updated = datetime.now()
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            raise
    
    def add_position(self, position: Position) -> None:
        """Add a position to the portfolio
        
        Args:
            position: Position to add
            
        Raises:
            ValueError: If position is invalid
        """
        try:
            if not isinstance(position, Position):
                raise ValueError("Must provide a Position object")
            if not hasattr(position, 'id'):
                raise ValueError("Position must have an 'id' attribute")
            self.positions.append(position)
            self.last_updated = datetime.now()
            self.update_metadata()
        except Exception as e:
            logger.error(f"Error adding position: {str(e)}")
            raise
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the portfolio
        
        Args:
            transaction: Transaction to add
            
        Raises:
            ValueError: If transaction is invalid
        """
        try:
            if not isinstance(transaction, Transaction):
                raise ValueError("Must provide a Transaction object")
            if not hasattr(transaction, 'id'):
                raise ValueError("Transaction must have an 'id' attribute")
            self.transactions.append(transaction)
            self.last_updated = datetime.now()
            self.update_metadata()
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            raise

    def get_position_by_symbol(self, symbol: str, position_type: str) -> Optional[Position]:
        """Get a position by symbol and type
        
        Args:
            symbol: Stock symbol
            position_type: Type of position
            
        Returns:
            Position if found, None otherwise
            
        Raises:
            ValueError: If inputs are invalid
        """
        try:
            if not symbol or not position_type:
                raise ValueError("Symbol and position_type must be provided")
            
            for position in self.positions:
                if (position.symbol == symbol.upper() and 
                    position.position_type == position_type):
                    return position
            return None
        except Exception as e:
            logger.error(f"Error getting position: {str(e)}")
            raise
    
    def to_dict(self) -> dict:
        """Convert portfolio to dictionary
        
        Returns:
            Dictionary representation of portfolio
        """
        try:
            return {
                'id': self.id,
                'positions': [p.to_dict() for p in self.positions],
                'transactions': [t.to_dict() for t in self.transactions],
                'metadata': self.metadata
            }
        except Exception as e:
            logger.error(f"Error converting portfolio to dict: {str(e)}")
            raise
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Portfolio':
        """Create portfolio from dictionary
        
        Args:
            data: Dictionary containing portfolio data
            
        Returns:
            New Portfolio instance
            
        Raises:
            ValueError: If data is invalid
        """
        try:
            return cls(
                portfolio_id=data.get('id'),
                positions=[Position.from_dict(p) for p in data.get('positions', [])],
                transactions=[Transaction.from_dict(t) for t in data.get('transactions', [])],
                metadata=data.get('metadata', {})
            )
        except Exception as e:
            logger.error(f"Error creating portfolio from dict: {str(e)}")
            raise

    def __str__(self) -> str:
        """String representation of portfolio"""
        return f"Portfolio(id={self.id}, positions={len(self.positions)}, transactions={len(self.transactions)})"