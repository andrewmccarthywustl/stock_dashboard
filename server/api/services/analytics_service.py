# server/api/services/analytics_service.py
from decimal import Decimal
from typing import Dict, List
from datetime import datetime, timedelta
from ..repositories import PortfolioRepository, TransactionRepository

class AnalyticsService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        transaction_repository: TransactionRepository
    ):
        self.portfolio_repo = portfolio_repository
        self.transaction_repo = transaction_repository

    def calculate_portfolio_metrics(self) -> Dict:
        """Calculate key portfolio metrics"""
        portfolio = self.portfolio_repo.get_default_portfolio()
        
        # Calculate beta-weighted exposure
        long_beta_exposure = sum(
            p.position_value * p.beta 
            for p in portfolio.positions 
            if p.position_type == "long"
        )
        
        short_beta_exposure = sum(
            p.position_value * p.beta 
            for p in portfolio.positions 
            if p.position_type == "short"
        )

        return {
            "long_beta_exposure": long_beta_exposure,
            "short_beta_exposure": short_beta_exposure,
            "net_beta_exposure": long_beta_exposure - short_beta_exposure,
            "long_short_ratio": portfolio.long_short_ratio,
            "sector_concentration": self._calculate_sector_concentration(portfolio.positions),
            "position_concentration": self._calculate_position_concentration(portfolio.positions)
        }

    def calculate_performance_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Calculate performance metrics for a date range"""
        transactions = self.transaction_repo.get_by_date_range(start_date, end_date)
        
        realized_gains = sum(
            t.realized_gain for t in transactions 
            if t.realized_gain is not None
        )
        
        # Calculate daily P&L
        daily_pnl = self._calculate_daily_pnl(transactions)
        
        # Calculate Sharpe ratio using daily P&L
        sharpe_ratio = self._calculate_sharpe_ratio(daily_pnl)

        return {
            "realized_gains": realized_gains,
            "sharpe_ratio": sharpe_ratio,
            "daily_pnl": daily_pnl,
            "win_rate": self._calculate_win_rate(transactions),
            "average_win": self._calculate_average_win(transactions),
            "average_loss": self._calculate_average_loss(transactions)
        }

    def _calculate_sector_concentration(self, positions: List) -> Dict:
        """Calculate sector concentration metrics"""
        sector_values = {}
        total_value = sum(p.position_value for p in positions)
        
        if total_value == 0:
            return {}

        for position in positions:
            sector = position.sector
            if sector not in sector_values:
                sector_values[sector] = 0
            sector_values[sector] += position.position_value

        return {
            sector: (value / total_value * 100)
            for sector, value in sector_values.items()
        }

    def _calculate_position_concentration(self, positions: List) -> Dict:
        """Calculate position concentration metrics"""
        if not positions:
            return {}

        total_value = sum(p.position_value for p in positions)
        if total_value == 0:
            return {}

        position_weights = [
            (p.symbol, p.position_value / total_value * 100)
            for p in positions
        ]
        
        return {
            "largest_position": max(position_weights, key=lambda x: x[1]),
            "top_5_positions": sorted(position_weights, key=lambda x: x[1], reverse=True)[:5]
        }

    def _calculate_daily_pnl(self, transactions: List) -> Dict[datetime, Decimal]:
        """Calculate daily profit/loss"""
        daily_pnl = {}
        
        for transaction in transactions:
            date = transaction.date.date()
            if date not in daily_pnl:
                daily_pnl[date] = Decimal('0')
            if transaction.realized_gain:
                daily_pnl[date] += transaction.realized_gain

        return daily_pnl

    def _calculate_sharpe_ratio(
        self,
        daily_pnl: Dict[datetime, Decimal],
        risk_free_rate: float = 0.02
    ) -> float:
        """Calculate Sharpe ratio using daily P&L"""
        if not daily_pnl:
            return 0.0

        daily_returns = list(daily_pnl.values())
        
        if not daily_returns:
            return 0.0

        import statistics
        mean_return = statistics.mean(daily_returns)
        std_dev = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
        
        if std_dev == 0:
            return 0.0

        daily_risk_free = risk_free_rate / 252  # Approximate trading days in a year
        sharpe = (mean_return - daily_risk_free) / std_dev
        return float(sharpe * (252 ** 0.5))  # Annualize

    def _calculate_win_rate(self, transactions: List) -> float:
        """Calculate win rate from transactions"""
        winning_trades = sum(
            1 for t in transactions 
            if t.realized_gain and t.realized_gain > 0
        )
        total_trades = sum(
            1 for t in transactions 
            if t.realized_gain is not None
        )
        
        return winning_trades / total_trades if total_trades > 0 else 0.0

    def _calculate_average_win(self, transactions: List) -> Decimal:
        """Calculate average winning trade size"""
        winning_trades = [
            t.realized_gain for t in transactions 
            if t.realized_gain and t.realized_gain > 0
        ]
        
        return sum(winning_trades) / len(winning_trades) if winning_trades else Decimal('0')

    def _calculate_average_loss(self, transactions: List) -> Decimal:
        """Calculate average losing trade size"""
        losing_trades = [
            t.realized_gain for t in transactions 
            if t.realized_gain and t.realized_gain < 0
        ]
        
        return sum(losing_trades) / len(losing_trades) if losing_trades else Decimal('0')