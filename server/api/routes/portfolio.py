# ./server/api/routes/portfolio.py

from flask import Blueprint, request, jsonify
from api.models.portfolio import Portfolio
from api.services.stock_service import StockService
from utils.api_helpers import APIError

portfolio_bp = Blueprint('portfolio', __name__)
portfolio = Portfolio()
stock_service = StockService()

@portfolio_bp.route('/get-portfolio', methods=['GET'])
@portfolio_bp.route('/get-portfolio', methods=['GET'])
def get_portfolio():
    try:
        portfolio.load_portfolio()
        print("Portfolio loaded successfully")
        print("Raw portfolio dataframe:")
        print(portfolio.portfolio_df)  # Print the raw dataframe
        
        stocks_dict = portfolio.portfolio_df.set_index('symbol').to_dict(orient='index')
        print("Converted portfolio dict:")
        print(stocks_dict)

        stocks_list = []
        for symbol, data in stocks_dict.items():
            print(f"Processing symbol {symbol}, data:", data)  # Debug each position
            position_data = {
                "symbol": symbol,
                "quantity": data["quantity"],
                "current_price": data["current_price"],
                "sector": data.get("sector", "Unknown"),
                "industry": data.get("industry", "Unknown"),
                "percent_change": round(data["percent_change"], 2),
                "position_type": data["position_type"],
                "position_value": abs(data["quantity"] * data["current_price"]),  # Make sure we use absolute value
                "cost_basis": round(portfolio.calculate_cost_basis(symbol, data["position_type"]), 2),
                "running_total_gains": round(portfolio.get_running_total(symbol), 2),
                "beta": data.get("beta", 0)
            }
            print(f"Created position data:", position_data)  # Debug the processed data
            stocks_list.append(position_data)

        response = {
            "metadata": {
                "total_long_value": round(portfolio.metadata["total_long_value"], 2),
                "total_short_value": round(portfolio.metadata["total_short_value"], 2),
                "long_short_ratio": (
                    round(portfolio.metadata["long_short_ratio"], 2) 
                    if isinstance(portfolio.metadata["long_short_ratio"], (int, float)) 
                    else "N/A"
                ),
                "long_positions_count": portfolio.metadata["long_positions_count"],
                "short_positions_count": portfolio.metadata["short_positions_count"],
                "weighted_long_beta": portfolio.metadata["weighted_long_beta"],
                "weighted_short_beta": portfolio.metadata["weighted_short_beta"],
                "total_realized_gains": round(portfolio.metadata["total_realized_gains"], 2),
                "last_updated": portfolio.metadata["last_updated"],
                "long_sectors": portfolio.metadata["long_sectors"],
                "short_sectors": portfolio.metadata["short_sectors"]
            },
            "stocks": stocks_list
        }
        print("Final response:", response)  # Debug final response

        return jsonify(response), 200

    except Exception as e:
        print("Error in /get-portfolio:", str(e))
        import traceback
        print("Traceback:", traceback.format_exc())
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

        # Add the stock and get the updated portfolio data
        portfolio.add_stock(stock_data)
        
        # Return updated portfolio data
        updated_portfolio = portfolio.get_portfolio_summary()
        
        return jsonify({
            "message": "Stock added successfully",
            "portfolio": updated_portfolio
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
        
        # Return updated portfolio data along with the sell result
        updated_portfolio = portfolio.get_portfolio_summary()

        return jsonify({
            "message": "Stock sold successfully",
            "result": {
                "realized_gain": round(result["realized_gain"], 2),
                "remaining_shares": result["remaining_shares"],
                "running_total_gains": round(result["running_total"], 2)
            },
            "portfolio": updated_portfolio
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

        portfolio.add_short_position(stock_data)
        
        # Return updated portfolio data
        updated_portfolio = portfolio.get_portfolio_summary()

        return jsonify({
            "message": "Short position opened successfully",
            "portfolio": updated_portfolio
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
        
        # Return updated portfolio data along with the cover result
        updated_portfolio = portfolio.get_portfolio_summary()

        return jsonify({
            "message": "Short position covered successfully",
            "result": {
                "realized_gain": round(result["realized_gain"], 2),
                "remaining_shares": result["remaining_shares"],
                "running_total_gains": round(result["running_total"], 2)
            },
            "portfolio": updated_portfolio
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
        
        # Return updated portfolio data
        updated_portfolio = portfolio.get_portfolio_summary()
        
        return jsonify({
            "message": "Prices updated successfully",
            "portfolio": updated_portfolio
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
        
        # Add beta to transaction data if it exists
        for t in transactions:
            if 'beta' not in t:
                try:
                    stock_info = stock_service.get_stock_info(t['symbol'])
                    t['beta'] = stock_info.get('beta', 0)
                except:
                    t['beta'] = 0
        
        return jsonify({
            "transactions": transactions,
            "total_count": len(transactions)
        }), 200
        
    except Exception as e:
        print(f"Error in get_transactions: {str(e)}")
        return jsonify({"error": str(e)}), 500