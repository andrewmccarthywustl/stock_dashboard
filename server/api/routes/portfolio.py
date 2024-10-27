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
        
        required_fields = ['stockSymbol', 'stockPurchaseDate', 'stockPurchaseQuantity', 'stockPurchasePrice']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing required fields",
                "required_fields": required_fields
            }), 400

        stock_data = {
            "symbol": data.get('stockSymbol').upper(),
            "purchase_date": data.get('stockPurchaseDate'),
            "quantity": float(data.get('stockPurchaseQuantity')),
            "buy_price": float(data.get('stockPurchasePrice')),
        }

        try:
            stock_info = stock_service.get_stock_info(stock_data["symbol"])
            stock_data.update({
                "sector": stock_info.get('sector'),
                "industry": stock_info.get('industry'),
                "current_price": stock_info.get('price'),
                "beta": stock_info.get('beta'),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except APIError as ae:
            return jsonify({"error": f"API Error: {str(ae)}"}), 503

        portfolio.add_stock(stock_data)

        cost_basis = portfolio.calculate_cost_basis(stock_data["symbol"])
        response = {
            "message": "Stock added successfully!",
            "portfolio_total_value": round(portfolio.metadata["total_value"], 2),
            "position_details": {
                "symbol": stock_data["symbol"],
                "total_shares": stock_data["quantity"],
                "average_cost": round(cost_basis, 2),
                "current_value": round(stock_data["quantity"] * stock_data["current_price"], 2),
                "sector": stock_data["sector"],
                "industry": stock_data["industry"]
            }
        }

        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Unexpected error in add_stock: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@portfolio_bp.route('/sell-stock', methods=['POST'])
def sell_stock():
    try:
        data = request.get_json()
        
        required_fields = ['stockSymbol', 'stockSellQuantity', 'stockSellPrice', 'stockSellDate']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing required fields",
                "required_fields": required_fields
            }), 400

        stock_data = {
            "symbol": data['stockSymbol'].upper(),
            "quantity": float(data['stockSellQuantity']),
            "price": float(data['stockSellPrice']),
            "date": data['stockSellDate']
        }

        result = portfolio.sell_stock(stock_data)

        response = {
            "message": "Stock sold successfully",
            "realized_gain": round(result["realized_gain"], 2),
            "remaining_shares": result["remaining_shares"],
            "running_total_gains": round(result["running_total"], 2),
            "portfolio_total_value": round(portfolio.metadata["total_value"], 2)
        }

        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in sell_stock: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@portfolio_bp.route('/update-prices', methods=['POST'])
def update_prices():
    try:
        portfolio.update_stock_prices()
        
        response = {
            "message": "Prices updated successfully",
            "metadata": {
                "total_value": round(portfolio.metadata["total_value"], 2),
                "total_realized_gains": round(portfolio.metadata["total_realized_gains"], 2),
                "last_updated": portfolio.metadata["last_updated"]
            }
        }
        
        return jsonify(response), 200
    
    except APIError as ae:
        return jsonify({"error": f"API Error: {str(ae)}"}), 503
    except Exception as e:
        print(f"Error in update_prices: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

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
        return jsonify({"error": "An unexpected error occurred"}), 500