from flask import Blueprint, jsonify, request
from api.services.stock_service import StockService
from api.services.news_service import NewsService
from utils.api_helpers import APIError

stock_bp = Blueprint('stock', __name__)
stock_service = StockService()
news_service = NewsService()

@stock_bp.route('/stock-info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get stock information"""
    try:
        stock_info = stock_service.get_stock_info(symbol)
        return jsonify(stock_info), 200
    except APIError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stock_bp.route('/stock-news/<symbol>', methods=['GET'])
def get_stock_news(symbol):
    """Get stock news"""
    try:
        news = news_service.get_stock_news(symbol)
        return jsonify({"news": news}), 200
    except APIError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500