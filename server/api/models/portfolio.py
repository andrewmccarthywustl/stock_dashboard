import pandas as pd
import json
import os
from datetime import datetime
from api.services.stock_service import StockService
from config.settings import Config

class Portfolio:
    def __init__(self):
        self.json_path = Config.PORTFOLIO_FILE
        self.portfolio_df = pd.DataFrame(columns=[
            'symbol', 'quantity', 'buy_price', 'current_price', 
            'sector', 'industry', 'percent_change'
        ])
        self.metadata = {
            "total_value": 0,
            "total_realized_gains": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions = []
        self.stock_service = StockService()
        self.load_portfolio()

    def load_portfolio(self):
        """Load portfolio data from JSON file"""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r') as file:
                    data = json.load(file)
                    self.metadata = data.get('metadata', self.metadata)
                    self.transactions = data.get('transactions', [])
                    portfolio_data = data.get('stocks', {})
                    
                    if portfolio_data:  # If there's data
                        self.portfolio_df = pd.DataFrame.from_dict(portfolio_data, orient='index').reset_index()
                        self.portfolio_df.rename(columns={'index': 'symbol'}, inplace=True)
                    else:  # If empty dict
                        self.portfolio_df = pd.DataFrame(columns=[
                            'symbol', 'quantity', 'buy_price', 'current_price', 
                            'sector', 'industry', 'percent_change'
                        ])
            else:
                print("Portfolio JSON file not found; initializing empty portfolio.")
                self.save_portfolio()  # Create the initial JSON file

        except Exception as e:
            print(f"Error loading portfolio: {e}")
            self.save_portfolio()

    def save_portfolio(self):
        """Save portfolio data to JSON file"""
        try:
            portfolio_dict = self.portfolio_df.set_index('symbol').to_dict(orient='index') if not self.portfolio_df.empty else {}
            
            data = {
                "metadata": self.metadata,
                "stocks": portfolio_dict,
                "transactions": self.transactions
            }
            
            with open(self.json_path, 'w') as file:
                json.dump(data, file, indent=4)
                
        except Exception as e:
            print(f"Error saving portfolio: {e}")

    def add_stock(self, stock_data):
        """Add stock to portfolio"""
        self._validate_stock_data(stock_data)
        
        # Create transaction record
        transaction = {
            "type": "buy",
            "symbol": stock_data["symbol"],
            "quantity": float(stock_data["quantity"]),
            "price": float(stock_data["buy_price"]),
            "date": stock_data["purchase_date"]
        }
        self.transactions.append(transaction)

        # Calculate percent change
        percent_change = ((stock_data["current_price"] - stock_data["buy_price"]) / stock_data["buy_price"]) * 100
        stock_data["percent_change"] = percent_change

        # Update portfolio
        if stock_data["symbol"] in self.portfolio_df['symbol'].values:
            # Update existing position
            idx = self.portfolio_df.index[self.portfolio_df['symbol'] == stock_data["symbol"]][0]
            self.portfolio_df.at[idx, 'quantity'] += float(stock_data["quantity"])
            # Update cost basis
            self.portfolio_df.at[idx, 'buy_price'] = self.calculate_cost_basis(stock_data["symbol"])
        else:
            # Add new position
            new_stock_df = pd.DataFrame([stock_data])
            self.portfolio_df = pd.concat([self.portfolio_df, new_stock_df], ignore_index=True)

        self.update_portfolio_metadata()
        self.save_portfolio()

    def sell_stock(self, stock_data):
        """Sell stock from portfolio"""
        self._validate_stock_data(stock_data, is_sell=True)
        
        symbol = stock_data['symbol']
        sell_quantity = float(stock_data['quantity'])
        sell_price = float(stock_data['price'])

        if symbol not in self.portfolio_df['symbol'].values:
            raise ValueError(f"Stock {symbol} not found in portfolio")

        current_position = self.portfolio_df.loc[self.portfolio_df['symbol'] == symbol].iloc[0]
        if sell_quantity > current_position['quantity']:
            raise ValueError(f"Insufficient shares to sell: have {current_position['quantity']}, trying to sell {sell_quantity}")

        # Calculate realized gain/loss
        cost_basis = self.calculate_cost_basis(symbol)
        realized_gain = (sell_price - cost_basis) * sell_quantity

        # Create transaction record
        transaction = {
            "type": "sell",
            "symbol": symbol,
            "quantity": sell_quantity,
            "price": sell_price,
            "date": stock_data['date'],
            "cost_basis": cost_basis,
            "realized_gain": realized_gain
        }
        self.transactions.append(transaction)

        # Update portfolio
        if sell_quantity == current_position['quantity']:
            self.portfolio_df = self.portfolio_df[self.portfolio_df['symbol'] != symbol]
        else:
            self.portfolio_df.loc[self.portfolio_df['symbol'] == symbol, 'quantity'] -= sell_quantity

        # Update metadata
        self.metadata["total_realized_gains"] += realized_gain
        self.update_portfolio_metadata()
        self.save_portfolio()

        return {
            "realized_gain": realized_gain,
            "remaining_shares": current_position['quantity'] - sell_quantity,
            "running_total": self.get_running_total(symbol)
        }

    def update_stock_prices(self):
        """Update current prices for all stocks"""
        if self.portfolio_df.empty:
            return
            
        symbols = self.portfolio_df['symbol'].tolist()
        try:
            updated_prices = self.stock_service.get_batch_quotes(symbols)
            
            for symbol, price in updated_prices.items():
                mask = self.portfolio_df['symbol'] == symbol
                self.portfolio_df.loc[mask, 'current_price'] = price
                self.portfolio_df.loc[mask, 'percent_change'] = (
                    (price - self.portfolio_df.loc[mask, 'buy_price'].iloc[0]) 
                    / self.portfolio_df.loc[mask, 'buy_price'].iloc[0] * 100
                )
                
            self.update_portfolio_metadata()
            self.save_portfolio()
            
        except Exception as e:
            print(f"Error updating prices: {str(e)}")
            raise

    def calculate_cost_basis(self, symbol):
        """Calculate the average cost basis for a symbol"""
        symbol_transactions = [t for t in self.transactions if t['symbol'] == symbol]
        total_shares = 0
        total_cost = 0
        
        for transaction in symbol_transactions:
            if transaction['type'] == 'buy':
                total_shares += transaction['quantity']
                total_cost += transaction['quantity'] * transaction['price']
            elif transaction['type'] == 'sell':
                total_shares -= transaction['quantity']
                # Adjust cost proportionally
                if total_shares > 0:
                    total_cost = (total_cost / (total_shares + transaction['quantity'])) * total_shares

        return total_cost / total_shares if total_shares > 0 else 0

    def get_running_total(self, symbol):
        """Get running total of realized gains/losses for a symbol"""
        return sum(t.get('realized_gain', 0) for t in self.transactions if t['symbol'] == symbol)

    def update_portfolio_metadata(self):
        """Update portfolio metadata"""
        if not self.portfolio_df.empty:
            self.portfolio_df['position_value'] = self.portfolio_df['quantity'] * self.portfolio_df['current_price']
            self.metadata["total_value"] = self.portfolio_df['position_value'].sum()
        else:
            self.metadata["total_value"] = 0
        self.metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _validate_stock_data(self, stock_data, is_sell=False):
        """Validate stock data"""
        required_fields = {
            'symbol': str,
            'quantity': (int, float),
            'price' if is_sell else 'buy_price': (int, float),
            'date' if is_sell else 'purchase_date': str
        }
        
        for field, field_type in required_fields.items():
            if field not in stock_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(stock_data[field], field_type):
                raise ValueError(f"Invalid type for {field}")
            
        if float(stock_data['quantity']) <= 0:
            raise ValueError("Quantity must be positive")
            
        price_field = 'price' if is_sell else 'buy_price'
        if float(stock_data[price_field]) <= 0:
            raise ValueError("Price must be positive")
            
        date_field = 'date' if is_sell else 'purchase_date'
        try:
            datetime.strptime(stock_data[date_field], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")