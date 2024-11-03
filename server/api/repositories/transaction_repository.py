# server/api/repositories/transaction_repository.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
import logging
from .json_repository import JSONRepository
from ..models import Transaction

class TransactionRepository(JSONRepository[Transaction]):
    """Repository for managing transaction history"""

    def __init__(self, file_path: str):
        """Initialize transaction repository with file path"""
        super().__init__(file_path, Transaction)
        self.logger = logging.getLogger(__name__)
        self._ensure_transaction_ids()

    def _ensure_transaction_ids(self) -> None:
        """Ensure all transactions have unique IDs"""
        next_id = 1
        for transaction in self.get_all():
            if not transaction.transaction_id:
                transaction.transaction_id = f"T{next_id}"
                next_id += 1
        self.save()

    def get_by_symbol(self, symbol: str) -> List[Transaction]:
        """Get all transactions for a specific symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of transactions for the symbol
        """
        if not symbol:
            return []
        return [
            t for t in self.get_all()
            if t.symbol.upper() == symbol.upper()
        ]

    def get_by_type(self, transaction_type: str) -> List[Transaction]:
        """Get all transactions of a specific type
        
        Args:
            transaction_type: Type of transaction (buy, sell, short, cover)
            
        Returns:
            List of transactions of the specified type
        """
        if not transaction_type or transaction_type not in Transaction.VALID_TRANSACTION_TYPES:
            return []
        return [
            t for t in self.get_all()
            if t.transaction_type == transaction_type
        ]

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Transaction]:
        """Get all transactions within a date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of transactions within the date range
        """
        if not start_date or not end_date or start_date > end_date:
            return []
        return [
            t for t in self.get_all()
            if start_date <= t.date <= end_date
        ]

    def get_realized_gains(self, symbol: Optional[str] = None) -> Decimal:
        """Calculate total realized gains, optionally filtered by symbol
        
        Args:
            symbol: Optional stock symbol to filter by
            
        Returns:
            Total realized gains/losses
        """
        transactions = (
            self.get_by_symbol(symbol) if symbol 
            else self.get_all()
        )
        return sum(
            (t.realized_gain or Decimal('0'))
            for t in transactions
        )

    def add_transaction(
        self,
        symbol: str,
        transaction_type: str,
        quantity: Decimal,
        price: Decimal,
        date: Optional[datetime] = None,
        realized_gain: Optional[Decimal] = None
    ) -> Transaction:
        """Add a new transaction with generated ID
        
        Args:
            symbol: Stock symbol
            transaction_type: Type of transaction
            quantity: Number of shares
            price: Price per share
            date: Transaction date (optional)
            realized_gain: Realized gain/loss (optional)
            
        Returns:
            New Transaction instance
        """
        if not date:
            date = datetime.now()

        # Generate new transaction ID
        existing_ids = set(
            int(t.transaction_id[1:]) 
            for t in self.get_all() 
            if t.transaction_id and t.transaction_id[1:].isdigit()
        )
        next_id = max(existing_ids, default=0) + 1

        transaction = Transaction(
            transaction_id=f"T{next_id}",
            symbol=symbol,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            date=date,
            realized_gain=realized_gain
        )
        
        return self.add(transaction)

    def get_transactions_by_criteria(
        self,
        symbol: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None
    ) -> List[Transaction]:
        """Get transactions matching multiple criteria
        
        Args:
            symbol: Stock symbol
            transaction_type: Type of transaction
            start_date: Start of date range
            end_date: End of date range
            min_amount: Minimum transaction amount
            max_amount: Maximum transaction amount
            
        Returns:
            List of matching transactions
        """
        transactions = self.get_all()

        if symbol:
            transactions = [t for t in transactions if t.symbol.upper() == symbol.upper()]
        if transaction_type:
            transactions = [t for t in transactions if t.transaction_type == transaction_type]
        if start_date and end_date:
            transactions = [t for t in transactions if start_date <= t.date <= end_date]
        if min_amount is not None:
            transactions = [t for t in transactions if t.total_value >= min_amount]
        if max_amount is not None:
            transactions = [t for t in transactions if t.total_value <= max_amount]

        return sorted(transactions, key=lambda t: t.date, reverse=True)

    def get_transaction_summary(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get summary of transactions with optional filters
        
        Args:
            symbol: Optional stock symbol to filter by
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dictionary containing transaction summary
        """
        transactions = self.get_all()

        # Apply filters
        if symbol:
            transactions = [t for t in transactions if t.symbol.upper() == symbol.upper()]
        if start_date and end_date:
            transactions = [t for t in transactions if start_date <= t.date <= end_date]

        # Calculate summary
        total_buys = sum(
            t.total_value for t in transactions 
            if t.transaction_type == 'buy'
        )
        total_sells = sum(
            t.total_value for t in transactions 
            if t.transaction_type == 'sell'
        )
        total_shorts = sum(
            t.total_value for t in transactions 
            if t.transaction_type == 'short'
        )
        total_covers = sum(
            t.total_value for t in transactions 
            if t.transaction_type == 'cover'
        )
        
        realized_gains = sum(
            (t.realized_gain or Decimal('0')) for t in transactions
        )

        return {
            'total_transactions': len(transactions),
            'total_buys': str(total_buys),
            'total_sells': str(total_sells),
            'total_shorts': str(total_shorts),
            'total_covers': str(total_covers),
            'realized_gains': str(realized_gains),
            'transaction_counts': {
                'buy': len([t for t in transactions if t.transaction_type == 'buy']),
                'sell': len([t for t in transactions if t.transaction_type == 'sell']),
                'short': len([t for t in transactions if t.transaction_type == 'short']),
                'cover': len([t for t in transactions if t.transaction_type == 'cover'])
            }
        }

    def delete_transactions_by_symbol(self, symbol: str) -> int:
        """Delete all transactions for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Number of transactions deleted
        """
        if not symbol:
            return 0
            
        transactions = self.get_by_symbol(symbol)
        count = 0
        for transaction in transactions:
            if self.delete(transaction.transaction_id):
                count += 1
        return count