# server/api/services/transaction_service.py
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict
from ..models import Transaction
from ..repositories import TransactionRepository, PortfolioRepository
import logging  

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository, portfolio_repository: PortfolioRepository):
        self.transaction_repo = transaction_repository
        self.portfolio_repo = portfolio_repository

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
        # Calculate total value
        total_value = quantity * price
        
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
        transactions = self.transaction_repo.get_transactions_by_criteria(
            symbol=symbol,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Ensure all transactions have calculated values
        for transaction in transactions:
            if hasattr(transaction, 'quantity') and hasattr(transaction, 'price'):
                transaction.total_value = transaction.quantity * transaction.price
            
        return transactions

    def get_transaction_summary(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get transaction summary with calculated values"""
        try:
            transactions = self.get_transactions(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            realized_gains = sum(
                t.realized_gain for t in transactions 
                if t.realized_gain is not None
            )
            
            return {
                'total_transactions': len(transactions),
                'realized_gains': str(realized_gains),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calculating transaction summary: {str(e)}")
            raise

    def get_realized_gains(self, symbol: Optional[str] = None) -> Decimal:
        """Get total realized gains"""
        return self.transaction_repo.get_realized_gains(symbol)