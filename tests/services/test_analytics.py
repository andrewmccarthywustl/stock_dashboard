# tests/services/test_analytics_service.py
import unittest
from decimal import Decimal
from datetime import datetime
from server.api.models import Portfolio, Position
from server.api.services import AnalyticsService
from server.api.repositories import PortfolioRepository, TransactionRepository

class MockPortfolioRepository:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def get_default_portfolio(self) -> Portfolio:
        return self.portfolio

class MockTransactionRepository:
    def __init__(self):
        self.transactions = []

class TestAnalyticsService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Create sample positions
        self.long_positions = [
            Position(
                symbol="AAPL",
                quantity=Decimal("100"),
                cost_basis=Decimal("150"),
                current_price=Decimal("160"),
                position_type="long",
                sector="Technology",
                industry="Consumer Electronics",
                beta=1.2,
                entry_date=datetime.now()
            ),
            Position(
                symbol="MSFT",
                quantity=Decimal("50"),
                cost_basis=Decimal("200"),
                current_price=Decimal("220"),
                position_type="long",
                sector="Technology",
                industry="Software",
                beta=1.1,
                entry_date=datetime.now()
            )
        ]

        self.short_positions = [
            Position(
                symbol="GME",
                quantity=Decimal("30"),
                cost_basis=Decimal("40"),
                current_price=Decimal("35"),
                position_type="short",
                sector="Consumer Cyclical",
                industry="Specialty Retail",
                beta=2.5,
                entry_date=datetime.now()
            )
        ]

        # Create portfolio with test positions
        self.portfolio = Portfolio(
            positions=self.long_positions + self.short_positions
        )

        # Initialize repositories with mock data
        self.portfolio_repo = MockPortfolioRepository(self.portfolio)
        self.transaction_repo = MockTransactionRepository()

        # Initialize service
        self.analytics_service = AnalyticsService(
            self.portfolio_repo,
            self.transaction_repo
        )

    def test_calculate_beta_exposure(self):
        """Test beta exposure calculations"""
        metrics = self.analytics_service.calculate_portfolio_metrics()

        # Calculate expected values
        # Long positions
        aapl_value = Decimal("100") * Decimal("160")  # 16000
        msft_value = Decimal("50") * Decimal("220")   # 11000
        total_long_value = aapl_value + msft_value    # 27000

        expected_long_beta = (
            (aapl_value / total_long_value) * Decimal("1.2") +
            (msft_value / total_long_value) * Decimal("1.1")
        )

        # Short positions
        gme_value = Decimal("30") * Decimal("35")
        total_short_value = gme_value
        expected_short_beta = Decimal("2.5")  # Only one position

        # Test long beta exposure
        self.assertAlmostEqual(
            float(metrics["long_beta_exposure"]),
            float(expected_long_beta),
            places=2
        )

        # Test short beta exposure
        self.assertAlmostEqual(
            float(metrics["short_beta_exposure"]),
            float(expected_short_beta),
            places=2
        )

        # Test net beta exposure
        self.assertAlmostEqual(
            float(metrics["net_beta_exposure"]),
            float(expected_long_beta - expected_short_beta),
            places=2
        )

    def test_calculate_long_short_ratio(self):
        """Test long/short ratio calculation"""
        metrics = self.analytics_service.calculate_portfolio_metrics()

        # Calculate expected values
        long_value = (
            Decimal("100") * Decimal("160") + 
            Decimal("50") * Decimal("220")
        )
        short_value = Decimal("30") * Decimal("35")
        expected_ratio = float(long_value / short_value if short_value else float('inf'))

        # Test ratio
        self.assertAlmostEqual(
            float(metrics["long_short_ratio"]),
            expected_ratio,
            places=2
        )

    def test_empty_portfolio(self):
        """Test calculations with empty portfolio"""
        empty_portfolio = Portfolio(positions=[])
        empty_repo = MockPortfolioRepository(empty_portfolio)
        service = AnalyticsService(empty_repo, self.transaction_repo)

        metrics = service.calculate_portfolio_metrics()

        # Test that metrics are properly handled for empty portfolio
        self.assertEqual(metrics["long_beta_exposure"], 0)
        self.assertEqual(metrics["short_beta_exposure"], 0)
        self.assertEqual(metrics["net_beta_exposure"], 0)
        self.assertEqual(metrics["long_short_ratio"], float('inf'))

    def test_sector_concentration(self):
        """Test sector concentration calculations"""
        metrics = self.analytics_service.calculate_portfolio_metrics()
        
        sector_concentration = metrics["sector_concentration"]
        
        # Verify Technology sector percentage
        tech_value = (
            Decimal("100") * Decimal("160") + 
            Decimal("50") * Decimal("220")
        )
        total_value = tech_value + (Decimal("30") * Decimal("35"))
        expected_tech_percentage = float(tech_value / total_value * 100)

        self.assertAlmostEqual(
            float(sector_concentration["Technology"]),
            expected_tech_percentage,
            places=2
        )

if __name__ == '__main__':
    unittest.main()