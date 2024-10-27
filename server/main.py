from flask import Flask
from flask_cors import CORS
from api.routes.portfolio import portfolio_bp
from api.routes.stock import stock_bp
from config.settings import Config

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8080)