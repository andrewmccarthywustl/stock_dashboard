# server/api/services/analytics_service.py
from decimal import Decimal
from typing import Dict, List
from datetime import datetime, timedelta
import logging
from ..repositories import PortfolioRepository, TransactionRepository

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        transaction_repository: TransactionRepository
    ):
        self.portfolio_repo = portfolio_repository
        self.transaction_repo = transaction_repository

    # server/api/services/analytics_service.py
    def calculate_portfolio_metrics(self) -> Dict:
        """Calculate key portfolio metrics"""
        try:
            portfolio = self.portfolio_repo.get_default_portfolio()
            
            # Calculate long positions metrics
            long_positions = [p for p in portfolio.positions if p.position_type == "long"]
            short_positions = [p for p in portfolio.positions if p.position_type == "short"]
            
            # Calculate total values using Decimal
            total_long_value = sum(p.position_value for p in long_positions)
            total_short_value = sum(p.position_value for p in short_positions)
            
            # Calculate beta exposures
            long_beta_exposure = Decimal('0')
            short_beta_exposure = Decimal('0')
            
            # Calculate weighted long beta
            if total_long_value > 0:
                long_beta_exposure = sum(
                    (p.position_value / total_long_value) * Decimal(str(p.beta))
                    for p in long_positions
                )
                
            # Calculate weighted short beta
            if total_short_value > 0:
                short_beta_exposure = sum(
                    (p.position_value / total_short_value) * Decimal(str(p.beta))
                    for p in short_positions
                )
                
            # Calculate long/short ratio
            long_short_ratio = None
            if total_short_value > Decimal('0'):
                long_short_ratio = float(total_long_value / total_short_value)
            elif total_long_value > Decimal('0'):
                long_short_ratio = float('inf')  # Only long positions
            else:
                long_short_ratio = 0.0  # No positions
            
            # Log the calculated values for debugging
            logger.info(f"Portfolio Analytics Calculation:")
            logger.info(f"Long Positions: {len(long_positions)}")
            logger.info(f"Short Positions: {len(short_positions)}")
            logger.info(f"Total Long Value: {total_long_value}")
            logger.info(f"Total Short Value: {total_short_value}")
            logger.info(f"Long Beta Exposure: {long_beta_exposure}")
            logger.info(f"Short Beta Exposure: {short_beta_exposure}")
            logger.info(f"Long/Short Ratio: {long_short_ratio}")
            
            return {
                "long_beta_exposure": float(round(long_beta_exposure, 2)),
                "short_beta_exposure": float(round(short_beta_exposure, 2)),
                "long_short_ratio": (
                    round(long_short_ratio, 2)
                    if long_short_ratio is not None and long_short_ratio != float('inf')
                    else 'N/A'
                ),
                "sector_concentration": self._calculate_sector_concentration(portfolio.positions),
                "position_concentration": self._calculate_position_concentration(portfolio.positions)
            }
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            logger.exception("Full traceback:")
            return {
                "long_beta_exposure": 0.0,
                "short_beta_exposure": 0.0,
                "long_short_ratio": "N/A",
                "sector_concentration": {},
                "position_concentration": {}
            }

    def _calculate_sector_concentration(self, positions: List) -> Dict:
        """Calculate sector concentration metrics"""
        try:
            sector_values = {}
            total_value = sum(p.position_value for p in positions)
            
            if total_value == 0:
                return {}

            for position in positions:
                sector = position.sector
                if sector not in sector_values:
                    sector_values[sector] = Decimal('0')
                sector_values[sector] += position.position_value

            return {
                sector: float(round((value / total_value * 100), 2))
                for sector, value in sector_values.items()
            }
        except Exception as e:
            logger.error(f"Error calculating sector concentration: {str(e)}")
            return {}

    def _calculate_position_concentration(self, positions: List) -> Dict:
        """Calculate position concentration metrics"""
        try:
            if not positions:
                return {}

            total_value = sum(p.position_value for p in positions)
            if total_value == 0:
                return {}

            position_weights = [
                (p.symbol, float(round((p.position_value / total_value * 100), 2)))
                for p in positions
            ]
            
            return {
                "largest_position": max(position_weights, key=lambda x: x[1]),
                "top_5_positions": sorted(position_weights, key=lambda x: x[1], reverse=True)[:5]
            }
        except Exception as e:
            logger.error(f"Error calculating position concentration: {str(e)}")
            return {}