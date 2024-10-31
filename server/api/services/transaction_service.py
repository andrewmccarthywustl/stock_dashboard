# server/api/services/transaction_service.py
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict
from ..models import Transaction
from ..repositories import TransactionRepository

class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repo = transaction_repository

    def add_transaction(
        self,
        symbol: str,
        transaction_type: str,
        quantity: Decimal,
        price: Decimal,
        date: Optional[datetime] = None,
        realized_gain: Optional[Decimal] = None
    ) -> Transaction:
        """Add a new transaction"""
        return self.transaction_repo.add_transaction(
            symbol=symbol,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            date=date or datetime.now(),
            realized_gain=realized_gain
        )

    def get_transactions(
        self,
        symbol: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get transactions with optional filters"""
        return self.transaction_repo.get_transactions_by_criteria(
            symbol=symbol,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )

    def get_transaction_summary(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get transaction summary"""
        return self.transaction_repo.get_transaction_summary(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )

    def get_realized_gains(self, symbol: Optional[str] = None) -> Decimal:
        """Get total realized gains"""
        return self.transaction_repo.get_realized_gains(symbol)