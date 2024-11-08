import os
import sys
import unittest
from decimal import Decimal
from datetime import datetime

# Get project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Import only what we need for testing
from server.api.models.portfolio import Portfolio
from server.api.models.position import Position
from server.api.models.transaction import Transaction
from server.api.services.analytics_service import AnalyticsService

class MockPortfolioRepository:
    """Mock repository for testing"""
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.calls = []

    def get_default_portfolio(self) -> Portfolio:
        self.calls.append(('get_default_portfolio',))
        return self.portfolio

class MockTransactionRepository:
    """Mock repository for testing"""
    def __init__(self, transactions=None):
        self.transactions = transactions or []
        self.calls = []

    def get_by_date_range(self, start_date, end_date):
        self.calls.append(('get_by_date_range', start_date, end_date))
        return self.transactions

class TestAnalyticsService(unittest.TestCase):
    """Test suite for AnalyticsService"""

    def setUp(self):
        """Set up test fixtures before each test"""
        # Create test positions
        self.test_date = datetime.now()
        
        self.long_positions = [
            Position(
                symbol='AAPL',
                quantity=Decimal('100'),
                cost_basis=Decimal('150'),
                current_price=Decimal('160'),
                position_type='long',
                sector='Technology',
                industry='Consumer Electronics',
                beta=1.2,
                entry_date=self.test_date
            ),
            Position(
                symbol='MSFT',
                quantity=Decimal('50'),
                cost_basis=Decimal('200'),
                current_price=Decimal('220'),
                position_type='long',
                sector='Technology',
                industry='Software',
                beta=1.1,
                entry_date=self.test_date
            )
        ]

        self.short_positions = [
            Position(
                symbol='GME',
                quantity=Decimal('30'),
                cost_basis=Decimal('40'),
                current_price=Decimal('35'),
                position_type='short',
                sector='Consumer Cyclical',
                industry='Specialty Retail',
                beta=2.5,
                entry_date=self.test_date
            )
        ]

        # Create portfolio with test positions
        self.portfolio = Portfolio(
            portfolio_id='test_portfolio',
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

    def test_calculate_portfolio_metrics(self):
        """Test portfolio metrics calculation"""
        metrics = self.analytics_service.calculate_portfolio_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('long_beta_exposure', metrics)
        self.assertIn('short_beta_exposure', metrics)
        self.assertIn('net_beta_exposure', metrics)
        self.assertIn('sector_concentration', metrics)

        # Test long beta exposure (AAPL and MSFT)
        aapl_value = Decimal('100') * Decimal('160')
        msft_value = Decimal('50') * Decimal('220')
        total_long_value = aapl_value + msft_value
        
        expected_long_beta = float(
            (aapl_value/total_long_value * Decimal('1.2')) +
            (msft_value/total_long_value * Decimal('1.1'))
        )
        
        self.assertAlmostEqual(
            metrics['long_beta_exposure'],
            expected_long_beta,
            places=2
        )

        # Test short beta exposure (GME)
        self.assertAlmostEqual(metrics['short_beta_exposure'], 2.5, places=2)

    def test_sector_concentration(self):
        """Test sector concentration calculations"""
        metrics = self.analytics_service.calculate_portfolio_metrics()
        
        self.assertIn('sector_concentration', metrics)
        sector_concentration = metrics['sector_concentration']
        
        # Calculate expected Technology sector percentage
        tech_value = (Decimal('100') * Decimal('160')) + (Decimal('50') * Decimal('220'))
        total_value = tech_value + (Decimal('30') * Decimal('35'))
        expected_tech_percentage = float(tech_value / total_value * 100)
        
        self.assertAlmostEqual(
            sector_concentration['Technology'],
            expected_tech_percentage,
            places=2
        )

    def test_empty_portfolio(self):
        """Test metrics with empty portfolio"""
        empty_portfolio = Portfolio(portfolio_id='empty_test')
        empty_repo = MockPortfolioRepository(empty_portfolio)
        service = AnalyticsService(empty_repo, self.transaction_repo)

        metrics = service.calculate_portfolio_metrics()
        
        self.assertEqual(metrics['long_beta_exposure'], 0)
        self.assertEqual(metrics['short_beta_exposure'], 0)
        self.assertEqual(metrics['net_beta_exposure'], 0)
        self.assertEqual(metrics['sector_concentration'], {})

    def tearDown(self):
        """Clean up after each test"""
        self.portfolio = None
        self.portfolio_repo = None
        self.transaction_repo = None
        self.analytics_service = None

if __name__ == '__main__':
    unittest.main()