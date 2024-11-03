# server/api/routes/portfolio_bp.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
import logging
from api.services.portfolio_service import PortfolioService
from api.services.analytics_service import AnalyticsService
from utils.api_helpers import validate_required_fields
from utils.async_helpers import async_route

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.record
def record_params(setup_state):
    portfolio_bp.portfolio_service = setup_state.options['portfolio_service']
    portfolio_bp.analytics_service = setup_state.options['analytics_service']

@portfolio_bp.route('/portfolio', methods=['GET'])
@async_route
async def get_portfolio():
    """Get portfolio summary"""
    try:
        # The portfolio_service.get_portfolio_summary() method needs to be async
        portfolio = portfolio_bp.portfolio_service.get_portfolio_summary()
        # Since it's not an async method, we don't await it
        logger.info(f"Portfolio data retrieved: {portfolio}")
        return jsonify(portfolio), 200
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/positions', methods=['GET'])
@async_route
async def get_positions():
    """Get all positions"""
    try:
        position_type = request.args.get('type')  # 'long' or 'short'
        # Get positions without await since it's not async
        positions = portfolio_bp.portfolio_service.get_all_positions()
        if position_type:
            positions = [p for p in positions if p.position_type == position_type]
        return jsonify([p.to_dict() for p in positions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/position/<symbol>/<position_type>', methods=['GET'])
@async_route
async def get_position(symbol: str, position_type: str):
    """Get specific position"""
    try:
        # Remove await since get_position is not async
        position = portfolio_bp.portfolio_service.get_position(symbol, position_type)
        if position:
            return jsonify(position.to_dict()), 200
        return jsonify({"error": "Position not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/trade', methods=['POST'])
@async_route
async def execute_trade():
    """Execute a trade"""
    logger.info("Received trade request")
    try:
        data = request.json
        logger.info(f"Trade request data: {data}")
        
        if not all(k in data for k in ['symbol', 'quantity', 'price', 'trade_type', 'date']):
            missing = [k for k in ['symbol', 'quantity', 'price', 'trade_type', 'date'] if k not in data]
            logger.error(f"Missing required fields: {missing}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        try:
            symbol = data['symbol'].upper()
            quantity = Decimal(str(data['quantity']))
            price = Decimal(str(data['price']))
            trade_type = data['trade_type'].lower()
            date = datetime.fromisoformat(data['date'])
            
            logger.info(f"Processing {trade_type} order for {quantity} shares of {symbol} at {price}")
            
            portfolio_service = portfolio_bp.portfolio_service
            
            trade_functions = {
                'buy': portfolio_service.execute_buy,
                'sell': portfolio_service.execute_sell,
                'short': portfolio_service.execute_short,
                'cover': portfolio_service.execute_cover
            }
            
            if trade_type not in trade_functions:
                logger.error(f"Invalid trade type: {trade_type}")
                return jsonify({"error": f"Invalid trade type: {trade_type}"}), 400
                
            # These methods are async, so we await them
            result = await trade_functions[trade_type](
                symbol=symbol,
                quantity=quantity,
                price=price,
                date=date
            )
            
            position, transaction = result
            logger.info(f"Trade executed successfully: {transaction.to_dict()}")
            
            return jsonify({
                "position": position.to_dict() if position else None,
                "transaction": transaction.to_dict(),
                "message": f"Successfully executed {trade_type} order for {quantity} shares of {symbol}"
            }), 200
            
        except ValueError as e:
            logger.error(f"Value error processing trade: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return jsonify({"error": "Internal server error processing trade"}), 500

    except Exception as e:
        logger.error(f"Error in trade endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/update-prices', methods=['POST'])
@async_route
async def update_prices():
    """Update all position prices"""
    try:
        # This method should be async
        updated_portfolio = await portfolio_bp.portfolio_service.update_portfolio()
        return jsonify(updated_portfolio.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/metrics', methods=['GET'])
@async_route
async def get_metrics():
    """Get portfolio metrics"""
    try:
        # Remove await since calculate_portfolio_metrics is not async
        metrics = portfolio_bp.analytics_service.calculate_portfolio_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/transactions', methods=['GET'])
@async_route
async def get_transactions():
    """Get transaction history"""
    try:
        symbol = request.args.get('symbol')
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        filters = {}
        if symbol:
            filters['symbol'] = symbol
        if transaction_type:
            filters['transaction_type'] = transaction_type
        if start_date:
            filters['start_date'] = datetime.fromisoformat(start_date)
        if end_date:
            filters['end_date'] = datetime.fromisoformat(end_date)
            
        # Remove await since get_position_history is not async
        transactions = portfolio_bp.portfolio_service.get_position_history(**filters)
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/sector-exposure', methods=['GET'])
@async_route
async def get_sector_exposure():
    """Get sector exposure"""
    try:
        # Remove await since get_portfolio_summary is not async
        portfolio = portfolio_bp.portfolio_service.get_portfolio_summary()
        exposure = portfolio['sector_exposure']
        return jsonify(exposure), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/beta-exposure', methods=['GET'])
@async_route
async def get_beta_exposure():
    """Get portfolio beta exposure"""
    try:
        # Remove await since calculate_portfolio_metrics is not async
        metrics = portfolio_bp.analytics_service.calculate_portfolio_metrics()
        beta_exposure = {
            'long_beta_exposure': metrics['long_beta_exposure'],
            'short_beta_exposure': metrics['short_beta_exposure'],
            'net_beta_exposure': metrics['net_beta_exposure']
        }
        return jsonify(beta_exposure), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500