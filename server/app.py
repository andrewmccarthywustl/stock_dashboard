# server/app.py
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from api.routes.portfolio_bp import portfolio_bp
from api.config.config import get_config
from api.services import (
    PortfolioService,
    PositionService,
    StockService,
    AnalyticsService
)
from api.repositories import (
    PortfolioRepository,
    TransactionRepository
)
from api.core.middleware import setup_middleware
from api.core.logging import setup_logging
from api.services.stock_providers.alpha_vantage import AlphaVantageProvider
import logging
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import atexit

def create_app(config_name=None):
    """Create and configure the Flask application"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    config.init_app(app)
    
    # Initialize logging
    setup_logging(app)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize CORS
        CORS(app)
        
        # Enable compression
        Compress(app)
        
        # Set up async support
        executor = ThreadPoolExecutor(max_workers=app.config.get('MAX_THREAD_POOL_SIZE', 20))
        app.executor = executor
        
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app.loop = loop
        
        # Register cleanup
        @atexit.register
        def cleanup():
            executor.shutdown(wait=True)
            if loop.is_running():
                loop.stop()
            if not loop.is_closed():
                loop.close()
        
        # Ensure data directories exist
        os.makedirs(app.config['DATA_DIR'], exist_ok=True)
        
        # Initialize repositories
        portfolio_repo = PortfolioRepository(
            os.path.join(app.config['DATA_DIR'], 'portfolio.json')
        )
        
        transaction_repo = TransactionRepository(
            os.path.join(app.config['DATA_DIR'], 'transactions.json')
        )
        
        # Initialize Alpha Vantage provider
        alpha_vantage_key = app.config.get('ALPHA_VANTAGE_API_KEY')
        if not alpha_vantage_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY must be set in configuration")
            
        stock_provider = AlphaVantageProvider(alpha_vantage_key)
        
        # Initialize stock service
        stock_service = StockService(stock_provider)
        
        # Store the stock provider for cleanup
        app.stock_provider = stock_provider
        
        # Initialize position service
        position_service = PositionService(
            portfolio_repo,
            stock_service
        )
        
        analytics_service = AnalyticsService(
            portfolio_repo,
            transaction_repo
        )
        
        portfolio_service = PortfolioService(
            portfolio_repo,
            transaction_repo,
            position_service,
            stock_service
        )
        
        # Store services in app context
        app.stock_service = stock_service
        app.portfolio_service = portfolio_service
        app.analytics_service = analytics_service
        
        # Setup middleware
        setup_middleware(app)
        
        # Register blueprints
        app.register_blueprint(
            portfolio_bp,
            url_prefix='/api/portfolio',
            portfolio_service=portfolio_service,
            analytics_service=analytics_service
        )
        
        # Request teardown to cleanup aiohttp sessions
        @app.teardown_appcontext
        async def cleanup_sessions(exception=None):
            if hasattr(app, 'stock_provider'):
                await app.stock_provider.cleanup()
        
        # Health check endpoint
        @app.route('/health')
        def health_check():
            return {
                'status': 'healthy',
                'version': app.config['API_VERSION']
            }
        
        logger.info(
            "Application initialized successfully",
            extra={
                'version': app.config['API_VERSION'],
                'environment': app.config['ENV']
            }
        )
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

def run_app():
    """Run the application"""
    app = create_app()
    
    try:
        host = app.config.get('HOST', '0.0.0.0')
        port = app.config.get('PORT', 8080)
        debug = app.config.get('DEBUG', False)
        
        logger = logging.getLogger(__name__)
        logger.info(
            f"Starting server on {host}:{port}",
            extra={
                'host': host,
                'port': port,
                'debug': debug,
                'env': app.config['ENV']
            }
        )
        
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=app.config.get('USE_RELOADER', True),
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to run application: {str(e)}")
        raise

if __name__ == "__main__":
    run_app()