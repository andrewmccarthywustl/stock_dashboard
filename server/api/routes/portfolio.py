# ./server/api/routes/portfolio.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from api.models.portfolio import Portfolio
from api.services.stock_service import StockService
from utils.api_helpers import APIError

portfolio_bp = Blueprint('portfolio', __name__)
portfolio = Portfolio()
stock_service = StockService()

@portfolio_bp.route('/get-portfolio', methods=['GET'])
def get_portfolio():
    try:
        portfolio.load_portfolio()
        stocks_dict = portfolio.portfolio_df.set_index('symbol').to_dict(orient='index')

        stocks_list = []
        for symbol, data in stocks_dict.items():
            position_data = {
                "symbol": symbol,
                "quantity": data["quantity"],
                "current_price": data["current_price"],
                "sector": data.get("sector", "Unknown"),
                "industry": data.get("industry", "Unknown"),
                "percent_change": round(data["percent_change"], 2),
                "position_value": round(data["quantity"] * data["current_price"], 2),
                "cost_basis": round(portfolio.calculate_cost_basis(symbol), 2),
                "running_total_gains": round(portfolio.get_running_total(symbol), 2)
            }
            stocks_list.append(position_data)

        total_value = portfolio.metadata["total_value"]
        sector_allocation = {}
        if total_value > 0:
            for stock in stocks_list:
                sector = stock["sector"]
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += (stock["position_value"] / total_value) * 100

        response = {
            "metadata": {
                "total_value": round(portfolio.metadata["total_value"], 2),
                "total_realized_gains": round(portfolio.metadata["total_realized_gains"], 2),
                "last_updated": portfolio.metadata["last_updated"],
                "sectors": sector_allocation,
                "total_positions": len(stocks_list)
            },
            "stocks": stocks_list
        }

        return jsonify(response), 200

    except Exception as e:
        print("Error in /get-portfolio:", str(e))
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/add-stock', methods=['POST'])
def add_stock():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug print
        
        # Validate with proper field names
        required_fields = ['stockSymbol', 'stockPurchaseQuantity', 'stockPurchasePrice', 'stockPurchaseDate']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
            if not data[field]:  # Check if field is empty
                return jsonify({
                    "error": f"Field cannot be empty: {field}"
                }), 400

        # Convert string values to proper types
        try:
            quantity = float(data['stockPurchaseQuantity'])
            price = float(data['stockPurchasePrice'])
        except ValueError:
            return jsonify({
                "error": "Invalid number format for quantity or price"
            }), 400

        stock_data = {
            "stockSymbol": data['stockSymbol'].upper(),
            "stockPurchaseQuantity": quantity,
            "stockPurchasePrice": price,
            "stockPurchaseDate": data['stockPurchaseDate']
        }

        # Get current price and other info
        try:
            stock_info = stock_service.get_stock_info(stock_data["stockSymbol"])
            stock_data.update({
                "current_price": stock_info.get('price'),
                "sector": stock_info.get('sector', 'Unknown'),
                "industry": stock_info.get('industry', 'Unknown'),
                "position_type": "long"
            })
        except APIError as ae:
            return jsonify({"error": f"API Error: {str(ae)}"}), 503

        portfolio.add_stock(stock_data)

        return jsonify({
            "message": "Stock added successfully",
            "data": stock_data
        }), 200

    except Exception as e:
        print(f"Error in add_stock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/sell-stock', methods=['POST'])
def sell_stock():
    try:
        data = request.get_json()
        
        required_fields = ['stockSymbol', 'stockSellQuantity', 'stockSellPrice', 'stockSellDate']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
            if not data[field]:
                return jsonify({
                    "error": f"Field cannot be empty: {field}"
                }), 400

        try:
            quantity = float(data['stockSellQuantity'])
            price = float(data['stockSellPrice'])
        except ValueError:
            return jsonify({
                "error": "Invalid number format for quantity or price"
            }), 400

        stock_data = {
            "stockSymbol": data['stockSymbol'].upper(),
            "stockSellQuantity": quantity,
            "stockSellPrice": price,
            "stockSellDate": data['stockSellDate']
        }

        result = portfolio.sell_stock(stock_data)

        return jsonify({
            "message": "Stock sold successfully",
            "data": {
                "realized_gain": round(result["realized_gain"], 2),
                "remaining_shares": result["remaining_shares"],
                "running_total_gains": round(result["running_total"], 2)
            }
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in sell_stock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/short-stock', methods=['POST'])
def short_stock():
    try:
        data = request.get_json()
        
        required_fields = ['stockSymbol', 'stockShortQuantity', 'stockShortPrice', 'stockShortDate']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
            if not data[field]:
                return jsonify({
                    "error": f"Field cannot be empty: {field}"
                }), 400

        try:
            quantity = float(data['stockShortQuantity'])
            price = float(data['stockShortPrice'])
        except ValueError:
            return jsonify({
                "error": "Invalid number format for quantity or price"
            }), 400

        stock_data = {
            "stockSymbol": data['stockSymbol'].upper(),
            "stockShortQuantity": quantity,
            "stockShortPrice": price,
            "stockShortDate": data['stockShortDate']
        }

        try:
            stock_info = stock_service.get_stock_info(stock_data["stockSymbol"])
            stock_data.update({
                "current_price": stock_info.get('price'),
                "sector": stock_info.get('sector', 'Unknown'),
                "industry": stock_info.get('industry', 'Unknown'),
                "position_type": "short"
            })
        except APIError as ae:
            return jsonify({"error": f"API Error: {str(ae)}"}), 503

        portfolio.add_short_position(stock_data)

        return jsonify({
            "message": "Short position opened successfully",
            "data": stock_data
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in short_stock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/cover-stock', methods=['POST'])
def cover_stock():
    try:
        data = request.get_json()
        
        required_fields = ['stockSymbol', 'stockCoverQuantity', 'stockCoverPrice', 'stockCoverDate']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
            if not data[field]:
                return jsonify({
                    "error": f"Field cannot be empty: {field}"
                }), 400

        try:
            quantity = float(data['stockCoverQuantity'])
            price = float(data['stockCoverPrice'])
        except ValueError:
            return jsonify({
                "error": "Invalid number format for quantity or price"
            }), 400

        stock_data = {
            "stockSymbol": data['stockSymbol'].upper(),
            "stockCoverQuantity": quantity,
            "stockCoverPrice": price,
            "stockCoverDate": data['stockCoverDate']
        }

        result = portfolio.cover_short(stock_data)

        return jsonify({
            "message": "Short position covered successfully",
            "data": {
                "realized_gain": round(result["realized_gain"], 2),
                "remaining_shares": result["remaining_shares"],
                "running_total_gains": round(result["running_total"], 2)
            }
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in cover_stock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/update-prices', methods=['POST'])
def update_prices():
    try:
        portfolio.update_stock_prices()
        
        return jsonify({
            "message": "Prices updated successfully",
            "metadata": {
                "total_value": round(portfolio.metadata["total_value"], 2),
                "total_realized_gains": round(portfolio.metadata["total_realized_gains"], 2),
                "last_updated": portfolio.metadata["last_updated"]
            }
        }), 200
    
    except APIError as ae:
        return jsonify({"error": f"API Error: {str(ae)}"}), 503
    except Exception as e:
        print(f"Error in update_prices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/get-transactions', methods=['GET'])
def get_transactions():
    try:
        symbol = request.args.get('symbol')
        transaction_type = request.args.get('type')
        
        transactions = portfolio.transactions
        
        if symbol:
            transactions = [t for t in transactions if t['symbol'].upper() == symbol.upper()]
        if transaction_type:
            transactions = [t for t in transactions if t['type'] == transaction_type]
            
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            "transactions": transactions,
            "total_count": len(transactions)
        }), 200
        
    except Exception as e:
        print(f"Error in get_transactions: {str(e)}")
        return jsonify({"error": str(e)}), 500