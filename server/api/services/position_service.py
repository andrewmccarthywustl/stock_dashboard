# server/api/services/position_service.py
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from ..models import Position
from ..repositories import PortfolioRepository
from .stock_service import StockService

class PositionService:
    def __init__(
        self, 
        portfolio_repository: PortfolioRepository,
        stock_service: StockService
    ):
        self.portfolio_repo = portfolio_repository
        self.stock_service = stock_service

    async def open_position(
        self,
        symbol: str,
        quantity: Decimal,
        position_type: str,
        cost_basis: Optional[Decimal] = None
    ) -> Position:
        """Open a new position"""
        # Get current stock info
        stock_info = await self.stock_service.get_stock_info(symbol)
        
        current_price = Decimal(str(stock_info['price']))
        
        # Use provided cost basis or current price
        actual_cost_basis = cost_basis if cost_basis is not None else current_price

        position = Position(
            symbol=symbol,
            quantity=quantity,
            cost_basis=actual_cost_basis,
            current_price=current_price,
            position_type=position_type,
            sector=stock_info.get('sector', 'Unknown'),
            industry=stock_info.get('industry', 'Unknown'),
            beta=stock_info.get('beta', 1.0),
            entry_date=datetime.now()
        )

        # Add position to portfolio
        updated_portfolio = self.portfolio_repo.add_position(position)
        return position

    def close_position(
        self,
        symbol: str,
        position_type: str
    ) -> Optional[Position]:
        """Close an existing position"""
        return self.portfolio_repo.close_position(symbol, position_type)

    async def update_position_price(
        self,
        symbol: str,
        position_type: str
    ) -> bool:
        """Update position's current price"""
        stock_info = await self.stock_service.get_stock_info(symbol)
        new_price = Decimal(str(stock_info['price']))
        
        return self.portfolio_repo.update_position_price(
            symbol,
            position_type,
            new_price
        )

    def get_position(
        self,
        symbol: str,
        position_type: str
    ) -> Optional[Position]:
        """Get a specific position"""
        return self.portfolio_repo.get_position(symbol, position_type)

    async def update_all_positions(self) -> List[Position]:
        """Update prices for all positions"""
        portfolio = self.portfolio_repo.get_default_portfolio()
        updated_positions = []

        for position in portfolio.positions:
            success = await self.update_position_price(
                position.symbol,
                position.position_type
            )
            if success:
                updated_position = self.get_position(
                    position.symbol,
                    position.position_type
                )
                if updated_position:
                    updated_positions.append(updated_position)

        return updated_positions

    def adjust_position_quantity(
        self,
        symbol: str,
        position_type: str,
        quantity_change: Decimal
    ) -> Optional[Position]:
        """Adjust the quantity of an existing position"""
        position = self.get_position(symbol, position_type)
        if not position:
            return None

        new_quantity = position.quantity + quantity_change
        if new_quantity <= 0:
            return self.close_position(symbol, position_type)

        # Calculate new cost basis (weighted average)
        if quantity_change > 0:
            total_value = (position.quantity * position.cost_basis +
                         quantity_change * position.current_price)
            new_cost_basis = total_value / new_quantity
            position.cost_basis = new_cost_basis

        position.quantity = new_quantity
        self.portfolio_repo.update(self.portfolio_repo.get_default_portfolio())
        return position