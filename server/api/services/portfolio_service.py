# server/api/services/portfolio_service.py
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from ..models import Portfolio, Position, Transaction
from ..repositories import PortfolioRepository, TransactionRepository
from .position_service import PositionService
from .stock_service import StockService

class PortfolioService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        transaction_repository: TransactionRepository,
        position_service: PositionService,
        stock_service: StockService
    ):
        self.portfolio_repo = portfolio_repository
        self.transaction_repo = transaction_repository
        self.position_service = position_service
        self.stock_service = stock_service
        self.logger = logging.getLogger(__name__)

    async def execute_buy(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        date: Optional[datetime] = None
    ) -> Tuple[Position, Transaction]:
        """Execute a buy order"""
        try:
            # Get stock info first
            stock_info = await self.stock_service.get_stock_info(symbol)
            
            # Create and save transaction
            transaction = self.transaction_repo.add_transaction(
                symbol=symbol,
                transaction_type="buy",
                quantity=quantity,
                price=price,
                date=date or datetime.now()
            )

            # Check for existing position
            position = self.portfolio_repo.get_position(symbol, "long")
            
            if position:
                # Update existing position
                new_quantity = position.quantity + quantity
                total_cost = (position.quantity * position.cost_basis) + (quantity * price)
                new_cost_basis = total_cost / new_quantity
                
                position.quantity = new_quantity
                position.cost_basis = new_cost_basis
                position.current_price = Decimal(str(stock_info['price']))
                position.last_updated = datetime.now()
                
                # Update position in portfolio
                self.portfolio_repo.update_position(position)
            else:
                # Create new position
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    cost_basis=price,
                    current_price=Decimal(str(stock_info['price'])),
                    position_type="long",
                    sector=stock_info.get('sector', 'Unknown'),
                    industry=stock_info.get('industry', 'Unknown'),
                    beta=float(stock_info.get('beta', 1.0)),
                    entry_date=date or datetime.now()
                )
                self.portfolio_repo.add_position(position)

            # Save portfolio changes
            self.portfolio_repo.save()
            
            return position, transaction
            
        except Exception as e:
            self.logger.error(f"Error executing buy order: {str(e)}")
            raise

    async def execute_sell(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        date: Optional[datetime] = None
    ) -> Tuple[Optional[Position], Transaction]:
        """Execute a sell order"""
        try:
            position = self.portfolio_repo.get_position(symbol, "long")
            if not position or position.quantity < quantity:
                raise ValueError(f"Insufficient shares to sell: {symbol}")

            # Calculate realized gain/loss
            realized_gain = (price - position.cost_basis) * quantity

            transaction = self.transaction_repo.add_transaction(
                symbol=symbol,
                transaction_type="sell",
                quantity=quantity,
                price=price,
                date=date or datetime.now(),
                realized_gain=realized_gain
            )

            if position.quantity == quantity:
                # Close position
                self.portfolio_repo.close_position(symbol, "long")
                position = None
            else:
                # Update position
                position.quantity -= quantity
                self.portfolio_repo.update_position(position)

            # Save portfolio changes
            self.portfolio_repo.save()
            
            return position, transaction
            
        except Exception as e:
            self.logger.error(f"Error executing sell order: {str(e)}")
            raise

    async def execute_short(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        date: Optional[datetime] = None
    ) -> Tuple[Position, Transaction]:
        """Execute a short sell order"""
        try:
            # Get stock info first
            stock_info = await self.stock_service.get_stock_info(symbol)
            
            # Create and save transaction
            transaction = self.transaction_repo.add_transaction(
                symbol=symbol,
                transaction_type="short",
                quantity=quantity,
                price=price,
                date=date or datetime.now()
            )

            # Check for existing position
            position = self.portfolio_repo.get_position(symbol, "short")
            
            if position:
                # Update existing position
                new_quantity = position.quantity + quantity
                total_cost = (position.quantity * position.cost_basis) + (quantity * price)
                new_cost_basis = total_cost / new_quantity
                
                position.quantity = new_quantity
                position.cost_basis = new_cost_basis
                position.current_price = Decimal(str(stock_info['price']))
                position.last_updated = datetime.now()
                
                # Update position in portfolio
                self.portfolio_repo.update_position(position)
            else:
                # Create new position
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    cost_basis=price,
                    current_price=Decimal(str(stock_info['price'])),
                    position_type="short",
                    sector=stock_info.get('sector', 'Unknown'),
                    industry=stock_info.get('industry', 'Unknown'),
                    beta=float(stock_info.get('beta', 1.0)),
                    entry_date=date or datetime.now()
                )
                self.portfolio_repo.add_position(position)

            # Save portfolio changes
            self.portfolio_repo.save()
            
            return position, transaction
            
        except Exception as e:
            self.logger.error(f"Error executing short order: {str(e)}")
            raise

    async def execute_cover(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        date: Optional[datetime] = None
    ) -> Tuple[Optional[Position], Transaction]:
        """Execute a short cover order"""
        try:
            position = self.portfolio_repo.get_position(symbol, "short")
            if not position or position.quantity < quantity:
                raise ValueError(f"Insufficient shares to cover: {symbol}")

            # Calculate realized gain/loss (reversed for short positions)
            realized_gain = (position.cost_basis - price) * quantity

            transaction = self.transaction_repo.add_transaction(
                symbol=symbol,
                transaction_type="cover",
                quantity=quantity,
                price=price,
                date=date or datetime.now(),
                realized_gain=realized_gain
            )

            if position.quantity == quantity:
                # Close position
                self.portfolio_repo.close_position(symbol, "short")
                position = None
            else:
                # Update position
                position.quantity -= quantity
                self.portfolio_repo.update_position(position)

            # Save portfolio changes
            self.portfolio_repo.save()
            
            return position, transaction
            
        except Exception as e:
            self.logger.error(f"Error executing cover order: {str(e)}")
            raise

    async def update_portfolio(self) -> Portfolio:
        """Update all positions in the portfolio with current prices"""
        try:
            portfolio = self.portfolio_repo.get_default_portfolio()
            symbols = [p.symbol for p in portfolio.positions]
            
            if not symbols:
                return portfolio

            # Get batch quotes for all symbols
            quotes = await self.stock_service.get_batch_quotes(symbols)
            
            for position in portfolio.positions:
                if position.symbol in quotes:
                    position.current_price = quotes[position.symbol]
                    position.last_updated = datetime.now()

            self.portfolio_repo.update(portfolio)
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Error updating portfolio: {str(e)}")
            raise

    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary including positions and performance metrics"""
        try:
            portfolio = self.portfolio_repo.get_default_portfolio()
            transactions = self.transaction_repo.get_all()

            total_realized_gains = sum(
                t.realized_gain for t in transactions 
                if t.realized_gain is not None
            )
            
            total_unrealized_gains = sum(
                p.unrealized_gains for p in portfolio.positions
            )

            return {
                "positions": [p.to_dict() for p in portfolio.positions],
                "metadata": {
                    "total_value": str(portfolio.total_long_value + portfolio.total_short_value),
                    "total_long_value": str(portfolio.total_long_value),
                    "total_short_value": str(portfolio.total_short_value),
                    "long_positions_count": len([p for p in portfolio.positions if p.position_type == "long"]),
                    "short_positions_count": len([p for p in portfolio.positions if p.position_type == "short"]),
                    "total_realized_gains": str(total_realized_gains),
                    "total_unrealized_gains": str(total_unrealized_gains),
                    "total_gains": str(total_realized_gains + total_unrealized_gains),
                    "long_sectors": portfolio.sector_exposure['long'],
                    "short_sectors": portfolio.sector_exposure['short'],
                    "last_updated": portfolio.last_updated.isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {str(e)}")
            raise

    def get_position_history(
        self,
        symbol: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get history of all transactions with optional filters"""
        try:
            transactions = self.transaction_repo.get_transactions_by_criteria(
                symbol=symbol,
                transaction_type=transaction_type,
                start_date=start_date,
                end_date=end_date
            )
            return [t.to_dict() for t in transactions]
        except Exception as e:
            self.logger.error(f"Error getting position history: {str(e)}")
            raise

    def get_all_positions(self) -> List[Position]:
        """Get all current positions"""
        try:
            portfolio = self.portfolio_repo.get_default_portfolio()
            return portfolio.positions
        except Exception as e:
            self.logger.error(f"Error getting all positions: {str(e)}")
            raise

    def get_total_exposure(self) -> Decimal:
        """Calculate total market exposure"""
        try:
            portfolio = self.portfolio_repo.get_default_portfolio()
            return portfolio.total_long_value + portfolio.total_short_value
        except Exception as e:
            self.logger.error(f"Error calculating total exposure: {str(e)}")
            raise