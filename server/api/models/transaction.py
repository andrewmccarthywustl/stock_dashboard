# server/api/models/transaction.py
from datetime import datetime
from decimal import Decimal
from typing import Optional
from .base_model import BaseModel

class Transaction(BaseModel):
    """Represents a transaction in the portfolio"""
    
    VALID_TRANSACTION_TYPES = {'buy', 'sell', 'short', 'cover'}
    
    def __init__(
        self,
        symbol: str,
        transaction_type: str,
        quantity: Decimal,
        price: Decimal,
        date: datetime,
        realized_gain: Optional[Decimal] = None,
        transaction_id: Optional[str] = None
    ):
        """Initialize a transaction
        
        Args:
            symbol: Stock symbol
            transaction_type: Type of transaction (buy, sell, short, cover)
            quantity: Number of shares
            price: Price per share
            date: Transaction date
            realized_gain: Realized gain/loss (optional)
            transaction_id: Unique identifier (optional)
        
        Raises:
            ValueError: If any input validation fails
        """
        # Validate inputs
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("Symbol must be a non-empty string")
        if transaction_type not in self.VALID_TRANSACTION_TYPES:
            raise ValueError(f"Transaction type must be one of {self.VALID_TRANSACTION_TYPES}")
        if not isinstance(quantity, Decimal) or quantity <= 0:
            raise ValueError("Quantity must be a positive decimal")
        if not isinstance(price, Decimal) or price <= 0:
            raise ValueError("Price must be a positive decimal")
        if realized_gain is not None and not isinstance(realized_gain, Decimal):
            raise ValueError("Realized gain must be a decimal or None")
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object")

        self.transaction_id = transaction_id
        self.symbol = symbol.upper()
        self.transaction_type = transaction_type
        self.quantity = Decimal(str(quantity))
        self.price = Decimal(str(price))
        self.date = date
        self.realized_gain = Decimal(str(realized_gain)) if realized_gain is not None else None

    @property
    def id(self) -> str:
        """Return transaction_id as id for JSONRepository compatibility"""
        return self.transaction_id
    
    @property
    def total_value(self) -> Decimal:
        """Calculate total transaction value"""
        return self.quantity * self.price

    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'symbol': self.symbol,
            'transaction_type': self.transaction_type,
            'quantity': str(self.quantity),
            'price': str(self.price),
            'date': self.date.isoformat(),
            'realized_gain': str(self.realized_gain) if self.realized_gain is not None else None,
            'total_value': str(self.total_value)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary
        
        Args:
            data: Dictionary containing transaction data
            
        Returns:
            New Transaction instance
        """
        return cls(
            transaction_id=data.get('transaction_id'),
            symbol=data['symbol'],
            transaction_type=data['transaction_type'],
            quantity=Decimal(data['quantity']),
            price=Decimal(data['price']),
            date=datetime.fromisoformat(data['date']),
            realized_gain=Decimal(data['realized_gain']) if data.get('realized_gain') else None
        )

    def __eq__(self, other: object) -> bool:
        """Compare two transactions for equality"""
        if not isinstance(other, Transaction):
            return NotImplemented
        return (
            self.transaction_id == other.transaction_id and
            self.symbol == other.symbol and
            self.transaction_type == other.transaction_type and
            self.quantity == other.quantity and
            self.price == other.price and
            self.date == other.date and
            self.realized_gain == other.realized_gain
        )

    def __repr__(self) -> str:
        """String representation of transaction"""
        return (
            f"Transaction(id={self.transaction_id}, "
            f"symbol={self.symbol}, "
            f"type={self.transaction_type}, "
            f"quantity={self.quantity}, "
            f"price={self.price}, "
            f"date={self.date.isoformat()}, "
            f"realized_gain={self.realized_gain})"
        )