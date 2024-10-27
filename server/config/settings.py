import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FMP_API_KEY = os.getenv("FMP_API_KEY")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    PORTFOLIO_FILE = os.path.join(DATA_DIR, 'portfolio.json')

    @staticmethod
    def validate():
        if not Config.FMP_API_KEY:
            raise ValueError("FMP_API_KEY is not set")
        if not Config.ALPHA_VANTAGE_API_KEY:
            raise ValueError("ALPHA_VANTAGE_API_KEY is not set")
        
        # Ensure data directory exists
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)