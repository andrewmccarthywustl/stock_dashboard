# server/app.py
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from redis import Redis
from api.routes.portfolio_bp import portfolio_bp
from api.config import get_config
from api.services import (
    PortfolioService,
    PositionService,
    StockService,
    AnalyticsService,
    CacheService
)
from api.repositories import (
    PortfolioRepository,
    TransactionRepository
)
from api.core.middleware import (
    setup_middleware,
    error_handler,
    rate_limiter,
    circuit_breaker
)
from api.core.logging import setup_logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os

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
        
        # Initialize Redis connection
        redis_client = Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            password=app.config['REDIS_PASSWORD'],
            decode_responses=True
        )
        
        # Initialize thread pool
        thread_pool = ThreadPoolExecutor(
            max_workers=app.config['MAX_THREAD_POOL_SIZE'],
            thread_name_prefix="AsyncWorker"
        )
        
        # Initialize services and repositories
        cache_service = CacheService(redis_client)
        
        # Ensure data directories exist
        os.makedirs(app.config['DATA_DIR'], exist_ok=True)
        
        # Initialize repositories
        portfolio_repo = PortfolioRepository(
            app.config['PORTFOLIO_FILE'],
            # cache_service=cache_service
        )
        
        transaction_repo = TransactionRepository(
            app.config['TRANSACTION_FILE'],
            # cache_service=cache_service
        )
        
        # Initialize services
        stock_service = StockService(
            app.config['FMP_API_KEY'],
            # cache_service=cache_service,
            # thread_pool=thread_pool
        )
        
        position_service = PositionService(
            portfolio_repo,
            stock_service,
            # cache_service=cache_service
        )
        
        analytics_service = AnalyticsService(
            portfolio_repo,
            transaction_repo,
            # cache_service=cache_service
        )
        
        portfolio_service = PortfolioService(
            portfolio_repo,
            transaction_repo,
            position_service,
            stock_service,
            # cache_service=cache_service,
            # thread_pool=thread_pool
        )
        
        # Setup middleware
        setup_middleware(app)
        
        # Register blueprints
        app.register_blueprint(
            portfolio_bp,
            url_prefix='/api/portfolio',
            portfolio_service=portfolio_service,
            analytics_service=analytics_service
        )
        
        # Health check endpoint
        @app.route('/health')
        def health_check():
            return {
                'status': 'healthy',
                'cache': cache_service.is_healthy(),
                'redis': redis_client.ping(),
                'version': app.config['API_VERSION']
            }
        
        # Error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return {
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }, 404

        @app.errorhandler(500)
        def internal_error(error):
            logger.exception("Internal server error")
            return {
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }, 500

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
        # Set up asyncio policy for Windows if needed
        if asyncio.get_event_loop_policy()._local._loop is None:
            asyncio.set_event_loop(asyncio.new_event_loop())
        
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