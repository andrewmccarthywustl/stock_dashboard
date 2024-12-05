# api/models/__init__.py
#TODO ADD MORE LOGGING
from decimal import Decimal
from datetime import datetime

# Export all models
from .base_model import BaseModel
from .position import Position
from .transaction import Transaction
from .portfolio import Portfolio

# Define version
__version__ = '1.0.0'

# Common type hints
from typing import Union, Optional

Number = Union[int, float, Decimal]

# Helper functions for model creation
def create_position(
    symbol: str,
    quantity: Number,
    cost_basis: Number,
    current_price: Number,
    position_type: str,
    sector: str,
    industry: str,
    beta: float,
    entry_date: Optional[datetime] = None,
    position_id: Optional[str] = None
) -> Position:
    """Helper function to create a Position with proper type conversion"""
    if entry_date is None:
        entry_date = datetime.now()
        
    return Position(
        symbol=symbol,
        quantity=Decimal(str(quantity)),
        cost_basis=Decimal(str(cost_basis)),
        current_price=Decimal(str(current_price)),
        position_type=position_type,
        sector=sector,
        industry=industry,
        beta=beta,
        entry_date=entry_date,
        position_id=position_id
    )

def create_transaction(
    symbol: str,
    transaction_type: str,
    quantity: Number,
    price: Number,
    date: Optional[datetime] = None,
    realized_gain: Optional[Number] = None,
    transaction_id: Optional[str] = None
) -> Transaction:
    """Helper function to create a Transaction with proper type conversion"""
    if date is None:
        date = datetime.now()
        
    return Transaction(
        symbol=symbol,
        transaction_type=transaction_type,
        quantity=Decimal(str(quantity)),
        price=Decimal(str(price)),
        date=date,
        realized_gain=Decimal(str(realized_gain)) if realized_gain is not None else None,
        transaction_id=transaction_id
    )

def create_portfolio(
    positions: Optional[list[Position]] = None,
    transactions: Optional[list[Transaction]] = None,
    portfolio_id: Optional[str] = None
) -> Portfolio:
    """Helper function to create a Portfolio"""
    return Portfolio(
        positions=positions or [],
        transactions=transactions or [],
        portfolio_id=portfolio_id
    )

# Export everything
__all__ = [
    'BaseModel',
    'Position',
    'Transaction',
    'Portfolio',
    'create_position',
    'create_transaction',
    'create_portfolio',
]