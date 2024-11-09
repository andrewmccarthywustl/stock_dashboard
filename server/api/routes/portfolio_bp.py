# server/api/routes/portfolio_bp.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
import logging
# from services.portfolio_service import PortfolioService
# from services.analytics_service import AnalyticsService
from utils.api_helpers import validate_required_fields
from utils.async_helpers import async_route
import asyncio

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
        # Get raw portfolio data first
        portfolio = portfolio_bp.portfolio_service.get_portfolio_summary()
        
        # Get analytics metrics
        analytics = portfolio_bp.analytics_service.calculate_portfolio_metrics()
        
        # Add analytics to metadata
        portfolio['metadata'].update({
            'long_beta_exposure': analytics['long_beta_exposure'],
            'short_beta_exposure': analytics['short_beta_exposure'],
            'long_short_ratio': analytics['long_short_ratio']
        })
        
        logger.info(f"Analytics metrics: {analytics}")
        logger.info(f"Portfolio metadata after update: {portfolio['metadata']}")
        
        return jsonify(portfolio), 200
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/trade', methods=['POST'])
@async_route
async def execute_trade():
    """Execute a trade"""
    logger.info("Received trade request")
    try:
        data = request.json
        logger.info(f"Trade request data: {data}")
        
        # Validate required fields
        required_fields = ['symbol', 'quantity', 'price', 'trade_type', 'date']
        validate_required_fields(data, required_fields)

        try:
            symbol = data['symbol'].upper()
            quantity = Decimal(str(data['quantity']))
            price = Decimal(str(data['price']))
            trade_type = data['trade_type'].lower()
            date = datetime.fromisoformat(data['date'])
            
            logger.info(f"Processing {trade_type} order for {quantity} shares of {symbol} at {price}")
            
            # Get stock info for new position
            stock_service = portfolio_bp.portfolio_service.stock_service
            stock_info = await stock_service.get_stock_info(symbol)
            
            portfolio_service = portfolio_bp.portfolio_service
            
            # Execute trade based on type
            trade_result = None
            if trade_type == 'buy':
                trade_result = await portfolio_service.execute_buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    date=date
                )
            elif trade_type == 'sell':
                trade_result = await portfolio_service.execute_sell(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    date=date
                )
            elif trade_type == 'short':
                trade_result = await portfolio_service.execute_short(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    date=date
                )
            elif trade_type == 'cover':
                trade_result = await portfolio_service.execute_cover(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    date=date
                )
            else:
                logger.error(f"Invalid trade type: {trade_type}")
                return jsonify({"error": f"Invalid trade type: {trade_type}"}), 400
            
            position, transaction = trade_result
            
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
        # Get all positions using the portfolio service
        positions = portfolio_bp.portfolio_service.get_all_positions()
        
        if not positions:
            return jsonify({"message": "No positions to update"}), 200
        
        # Get symbols
        symbols = [p.symbol for p in positions]
        
        # Get updated prices
        stock_service = portfolio_bp.portfolio_service.stock_service
        prices = await stock_service.get_batch_quotes(symbols)
        
        # Update each position's price
        updated_count = 0
        for position in positions:
            if position.symbol in prices:
                # Just await the update_position_price method with only the symbol
                await portfolio_bp.portfolio_service.position_service.update_position_price(
                    position.symbol,
                    position.position_type  # Keep position type for future compatibility
                )
                updated_count += 1
        
        return jsonify({
            "message": "Prices updated successfully",
            "updated_count": updated_count,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error updating prices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/metrics', methods=['GET'])
@async_route
async def get_metrics():
    """Get portfolio metrics"""
    try:
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
            
        # Get transactions with their total values calculated
        transactions = portfolio_bp.portfolio_service.get_position_history(**filters)
        
        # Calculate summary stats
        total_value = sum(Decimal(str(t.get('total_value', 0))) for t in transactions)
        realized_gains = sum(
            Decimal(str(t.get('realized_gain', 0))) 
            for t in transactions 
            if t.get('realized_gain') is not None
        )
        
        summary = {
            'total_value': str(total_value),
            'realized_gains': str(realized_gains),
            'total_transactions': len(transactions),
            'last_updated': datetime.now().isoformat(),
            'transaction_counts': {
                'buy': len([t for t in transactions if t.get('transaction_type') == 'buy']),
                'sell': len([t for t in transactions if t.get('transaction_type') == 'sell']),
                'short': len([t for t in transactions if t.get('transaction_type') == 'short']),
                'cover': len([t for t in transactions if t.get('transaction_type') == 'cover'])
            }
        }
        
        logger.info(f"Transaction summary calculated: {summary}")
        
        return jsonify({
            'transactions': transactions,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/sector-exposure', methods=['GET'])
@async_route
async def get_sector_exposure():
    """Get sector exposure"""
    try:
        portfolio = portfolio_bp.portfolio_service.get_portfolio_summary()
        exposure = portfolio['metadata'].get('sector_exposure', {
            'long': {},
            'short': {}
        })
        return jsonify(exposure), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/beta-exposure', methods=['GET'])
@async_route
async def get_beta_exposure():
    """Get portfolio beta exposure"""
    try:
        metrics = portfolio_bp.analytics_service.calculate_portfolio_metrics()
        beta_exposure = {
            'long_beta_exposure': metrics['long_beta_exposure'],
            'short_beta_exposure': metrics['short_beta_exposure'],
            'net_beta_exposure': metrics['net_beta_exposure']
        }
        return jsonify(beta_exposure), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500