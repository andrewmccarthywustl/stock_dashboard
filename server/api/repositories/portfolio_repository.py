# server/api/repositories/portfolio_repository.py
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime
import logging
from pathlib import Path
import json
from .json_repository import JSONRepository
from ..models import Portfolio, Position, Transaction

logger = logging.getLogger(__name__)

class PortfolioRepository(JSONRepository[Portfolio]):
    """Repository for managing portfolio data"""

    DEFAULT_ID = "default"

    def __init__(self, file_path: str):
        """Initialize portfolio repository with file path"""
        super().__init__(file_path, Portfolio)
        self.logger = logging.getLogger(__name__)
        self._ensure_data_file()
        self._ensure_default_portfolio()

    def _ensure_data_file(self) -> None:
        """Ensure the data file exists with proper initial structure"""
        try:
            data_file = Path(self.file_path)
            if not data_file.exists():
                initial_data = {
                    self.DEFAULT_ID: {
                        "id": self.DEFAULT_ID,
                        "positions": [],
                        "transactions": [],
                        "metadata": {
                            "total_long_value": "0",
                            "total_short_value": "0",
                            "long_short_ratio": "N/A",
                            "total_realized_gains": "0",
                            "last_updated": datetime.now().isoformat(),
                            "sector_exposure": {
                                "long": {},
                                "short": {}
                            },
                            "long_positions_count": 0,
                            "short_positions_count": 0,
                            "weighted_long_beta": "0",
                            "weighted_short_beta": "0"
                        }
                    }
                }
                data_file.parent.mkdir(parents=True, exist_ok=True)
                with data_file.open('w') as f:
                    json.dump(initial_data, f, indent=4)
        except Exception as e:
            logger.error(f"Error ensuring data file: {str(e)}")
            raise

    def _create_default_portfolio(self) -> Portfolio:
        """Create a new default portfolio with initial data structure"""
        try:
            return Portfolio(
                portfolio_id=self.DEFAULT_ID,
                positions=[],
                transactions=[],
                metadata={
                    "total_long_value": "0",
                    "total_short_value": "0",
                    "long_short_ratio": "N/A",
                    "total_realized_gains": "0",
                    "last_updated": datetime.now().isoformat(),
                    "sector_exposure": {
                        "long": {},
                        "short": {}
                    },
                    "long_positions_count": 0,
                    "short_positions_count": 0,
                    "weighted_long_beta": "0",
                    "weighted_short_beta": "0"
                }
            )
        except Exception as e:
            self.logger.error(f"Error creating default portfolio: {str(e)}")
            raise

    def _ensure_default_portfolio(self) -> None:
        """Ensure a default portfolio exists with proper structure"""
        try:
            if self.DEFAULT_ID not in self.entities:
                self.logger.info("Creating default portfolio")
                portfolio = self._create_default_portfolio()
                self.entities[self.DEFAULT_ID] = portfolio
                self.save()
        except Exception as e:
            self.logger.error(f"Error ensuring default portfolio: {str(e)}")
            raise

    def get_default_portfolio(self) -> Portfolio:
        """Get the default portfolio, creating it if it doesn't exist"""
        try:
            self._ensure_default_portfolio()
            return self.entities[self.DEFAULT_ID]
        except Exception as e:
            self.logger.error(f"Error getting default portfolio: {str(e)}")
            raise

    def update_position(self, position: Position) -> None:
        """Update a position in the portfolio"""
        try:
            portfolio = self.get_default_portfolio()
            updated = False
            
            for i, pos in enumerate(portfolio.positions):
                if pos.symbol == position.symbol and pos.position_type == position.position_type:
                    portfolio.positions[i] = position
                    updated = True
                    break
                    
            if not updated:
                portfolio.positions.append(position)
                
            portfolio.update_metadata()
            self.entities[self.DEFAULT_ID] = portfolio
            self.save()
            
        except Exception as e:
            self.logger.error(f"Error updating position: {str(e)}")
            raise

    def add_position(self, position: Position) -> None:
        """Add a position to the portfolio"""
        try:
            portfolio = self.get_default_portfolio()
            portfolio.positions.append(position)
            portfolio.update_metadata()
            self.entities[self.DEFAULT_ID] = portfolio
            self.save()
        except Exception as e:
            self.logger.error(f"Error adding position: {str(e)}")
            raise

    def close_position(self, symbol: str, position_type: str) -> Optional[Position]:
        """Remove a position from the portfolio"""
        try:
            portfolio = self.get_default_portfolio()
            position = None
            for i, pos in enumerate(portfolio.positions):
                if pos.symbol == symbol and pos.position_type == position_type:
                    position = portfolio.positions.pop(i)
                    break
            
            if position:
                portfolio.update_metadata()
                self.entities[self.DEFAULT_ID] = portfolio
                self.save()
            
            return position
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            raise

    def get_position(self, symbol: str, position_type: str) -> Optional[Position]:
        """Get a specific position"""
        try:
            portfolio = self.get_default_portfolio()
            for position in portfolio.positions:
                if position.symbol == symbol and position.position_type == position_type:
                    return position
            return None
        except Exception as e:
            self.logger.error(f"Error getting position: {str(e)}")
            raise

    def get_all_positions(self) -> List[Position]:
        """Get all positions in the portfolio"""
        try:
            portfolio = self.get_default_portfolio()
            return portfolio.positions
        except Exception as e:
            self.logger.error(f"Error getting all positions: {str(e)}")
            raise

    def get_positions_by_type(self, position_type: str) -> List[Position]:
        """Get all positions of a specific type"""
        try:
            portfolio = self.get_default_portfolio()
            return [p for p in portfolio.positions if p.position_type == position_type]
        except Exception as e:
            self.logger.error(f"Error getting positions by type: {str(e)}")
            raise

    def get_sector_exposure(self) -> Dict[str, Dict[str, float]]:
        """Get sector exposure for long and short positions"""
        try:
            portfolio = self.get_default_portfolio()
            return portfolio.sector_exposure
        except Exception as e:
            self.logger.error(f"Error getting sector exposure: {str(e)}")
            raise

    def get_portfolio_value(self) -> Dict[str, Decimal]:
        """Get total portfolio value breakdown"""
        try:
            portfolio = self.get_default_portfolio()
            return {
                "total_long_value": portfolio.total_long_value,
                "total_short_value": portfolio.total_short_value,
                "net_value": portfolio.total_long_value - portfolio.total_short_value
            }
        except Exception as e:
            self.logger.error(f"Error getting portfolio value: {str(e)}")
            raise

    def get_beta_exposure(self) -> Dict[str, float]:
        """Calculate portfolio beta exposure"""
        try:
            portfolio = self.get_default_portfolio()
            long_positions = [p for p in portfolio.positions if p.position_type == "long"]
            short_positions = [p for p in portfolio.positions if p.position_type == "short"]

            total_long_value = sum(p.position_value for p in long_positions)
            total_short_value = sum(p.position_value for p in short_positions)

            if total_long_value > 0:
                long_beta = sum(p.beta * float(p.position_value) for p in long_positions) / float(total_long_value)
            else:
                long_beta = 0

            if total_short_value > 0:
                short_beta = sum(p.beta * float(p.position_value) for p in short_positions) / float(total_short_value)
            else:
                short_beta = 0

            return {
                "long_beta": long_beta,
                "short_beta": short_beta,
                "net_beta": long_beta - short_beta
            }
        except Exception as e:
            self.logger.error(f"Error calculating beta exposure: {str(e)}")
            raise

    def save(self) -> None:
        """Save the portfolio to the JSON file"""
        try:
            super().save()
        except Exception as e:
            self.logger.error(f"Error saving portfolio: {str(e)}")
            raise

    def update(self, portfolio: Portfolio) -> Portfolio:
        """Update the portfolio, ensuring it uses the default ID"""
        try:
            if not isinstance(portfolio, Portfolio):
                raise ValueError("Must provide a Portfolio object")
            self.entities[self.DEFAULT_ID] = portfolio
            self.save()
            return portfolio
        except Exception as e:
            self.logger.error(f"Error updating portfolio: {str(e)}")
            raise