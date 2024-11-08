# server/api/models/position.py
from datetime import datetime
from decimal import Decimal
from typing import Optional
import logging
from uuid import uuid4
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class Position(BaseModel):
    """Represents a position in the portfolio"""
    
    VALID_POSITION_TYPES = {'long', 'short'}
    
    def __init__(
        self,
        symbol: str,
        quantity: Decimal,
        cost_basis: Decimal,
        current_price: Decimal,
        position_type: str,
        sector: str,
        industry: str,
        beta: float,
        entry_date: datetime,
        position_id: Optional[str] = None
    ):
        """Initialize a position
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            cost_basis: Average cost per share
            current_price: Current market price
            position_type: Type of position (long/short)
            sector: Stock sector
            industry: Stock industry
            beta: Stock beta
            entry_date: Position entry date
            position_id: Optional position identifier
            
        Raises:
            ValueError: If any input validation fails
        """
        try:
            # Validate inputs
            if not isinstance(symbol, str) or not symbol:
                raise ValueError("Symbol must be a non-empty string")
            if not isinstance(quantity, Decimal) or quantity <= 0:
                raise ValueError("Quantity must be a positive decimal")
            if not isinstance(cost_basis, Decimal) or cost_basis <= 0:
                raise ValueError("Cost basis must be a positive decimal")
            if not isinstance(current_price, Decimal) or current_price <= 0:
                raise ValueError("Current price must be a positive decimal")
            if position_type not in self.VALID_POSITION_TYPES:
                raise ValueError(f"Position type must be one of {self.VALID_POSITION_TYPES}")
            if not isinstance(beta, (int, float)) or beta < -1 or beta > 5:
                raise ValueError("Beta must be a number between 0 and 5")
            if not isinstance(entry_date, datetime):
                raise ValueError("Entry date must be a datetime object")

            self._position_id = position_id or f"POS_{str(uuid4())[:8]}"
            self.symbol = symbol.upper()
            self.quantity = Decimal(str(quantity))
            self.cost_basis = Decimal(str(cost_basis))
            self.current_price = Decimal(str(current_price))
            self.position_type = position_type
            self.sector = sector
            self.industry = industry
            self.beta = float(beta)
            self.entry_date = entry_date
            self.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error initializing position: {str(e)}")
            raise
    
    @property
    def id(self) -> str:
        """Get position ID for repository compatibility
        
        Returns:
            Position identifier
        """
        return self._position_id
    
    @property
    def position_value(self) -> Decimal:
        """Calculate current position value
        
        Returns:
            Current position value
        """
        try:
            return abs(self.quantity * self.current_price)
        except Exception as e:
            logger.error(f"Error calculating position value: {str(e)}")
            return Decimal('0')
    
    @property
    def percent_change(self) -> float:
        """Calculate percentage change
        
        Returns:
            Percentage change in position value
        """
        try:
            multiplier = -1 if self.position_type == 'short' else 1
            return float(
                multiplier * ((self.current_price - self.cost_basis) / self.cost_basis * 100)
            )
        except Exception as e:
            logger.error(f"Error calculating percent change: {str(e)}")
            return 0.0
    
    @property
    def unrealized_gains(self) -> Decimal:
        """Calculate unrealized gains/losses
        
        Returns:
            Unrealized gains/losses
        """
        try:
            multiplier = -1 if self.position_type == 'short' else 1
            return multiplier * (self.current_price - self.cost_basis) * self.quantity
        except Exception as e:
            logger.error(f"Error calculating unrealized gains: {str(e)}")
            return Decimal('0')
    
    def update_price(self, new_price: Decimal) -> None:
        """Update the current price
        
        Args:
            new_price: New market price
            
        Raises:
            ValueError: If price is invalid
        """
        try:
            if not isinstance(new_price, Decimal) or new_price <= 0:
                raise ValueError("New price must be a positive decimal")
            self.current_price = Decimal(str(new_price))
            self.last_updated = datetime.now()
        except Exception as e:
            logger.error(f"Error updating price: {str(e)}")
            raise
    
    def update_quantity(self, quantity_change: Decimal) -> None:
        """Update position quantity
        
        Args:
            quantity_change: Change in quantity (positive or negative)
            
        Raises:
            ValueError: If resulting quantity would be negative
        """
        try:
            new_quantity = self.quantity + quantity_change
            if new_quantity <= 0:
                raise ValueError("Position quantity cannot be negative")
            self.quantity = new_quantity
            self.last_updated = datetime.now()
        except Exception as e:
            logger.error(f"Error updating quantity: {str(e)}")
            raise
    
    def to_dict(self) -> dict:
        """Convert position to dictionary
        
        Returns:
            Dictionary representation of position
        """
        try:
            return {
                'position_id': self.id,
                'symbol': self.symbol,
                'quantity': str(self.quantity),
                'cost_basis': str(self.cost_basis),
                'current_price': str(self.current_price),
                'position_type': self.position_type,
                'sector': self.sector,
                'industry': self.industry,
                'beta': self.beta,
                'entry_date': self.entry_date.isoformat(),
                'last_updated': self.last_updated.isoformat(),
                'position_value': str(self.position_value),
                'percent_change': self.percent_change,
                'unrealized_gains': str(self.unrealized_gains)
            }
        except Exception as e:
            logger.error(f"Error converting position to dict: {str(e)}")
            raise
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create position from dictionary
        
        Args:
            data: Dictionary containing position data
            
        Returns:
            New Position instance
        """
        try:
            return cls(
                position_id=data.get('position_id'),
                symbol=data['symbol'],
                quantity=Decimal(data['quantity']),
                cost_basis=Decimal(data['cost_basis']),
                current_price=Decimal(data['current_price']),
                position_type=data['position_type'],
                sector=data['sector'],
                industry=data['industry'],
                beta=float(data['beta']),
                entry_date=datetime.fromisoformat(data['entry_date'])
            )
        except Exception as e:
            logger.error(f"Error creating position from dict: {str(e)}")
            raise

    def __eq__(self, other: object) -> bool:
        """Compare two positions for equality"""
        if not isinstance(other, Position):
            return NotImplemented
        return (
            self.id == other.id and
            self.symbol == other.symbol and
            self.position_type == other.position_type and
            self.quantity == other.quantity and
            self.cost_basis == other.cost_basis and
            self.current_price == other.current_price
        )

    def __str__(self) -> str:
        """String representation of position"""
        return (
            f"Position(id={self.id}, "
            f"symbol={self.symbol}, "
            f"type={self.position_type}, "
            f"quantity={self.quantity}, "
            f"value={self.position_value})"
        )