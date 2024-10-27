# ./server/api/models/portfolio.py

import pandas as pd
import json
import os
from datetime import datetime
from api.services.stock_service import StockService
from config.settings import Config

class Portfolio:
    def __init__(self):
        self.json_path = Config.PORTFOLIO_FILE
        # Define all columns explicitly
        self.columns = [
            'symbol', 
            'quantity', 
            'price', 
            'current_price', 
            'sector', 
            'industry', 
            'percent_change', 
            'position_type',
            'position_value'
        ]
        # Initialize empty DataFrame with all columns
        self.portfolio_df = pd.DataFrame(columns=self.columns)
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
                        self.portfolio_df = pd.DataFrame.from_dict(portfolio_data, orient='index')
                        self.portfolio_df.reset_index(inplace=True)
                        self.portfolio_df.rename(columns={'index': 'symbol'}, inplace=True)
                        
                        # Ensure all required columns exist
                        for col in self.columns:
                            if col not in self.portfolio_df.columns:
                                self.portfolio_df[col] = None
                    else:  # If empty dict
                        self.portfolio_df = pd.DataFrame(columns=self.columns)
                        
            else:
                print("Portfolio JSON file not found; initializing empty portfolio.")
                self.save_portfolio()  # Create the initial JSON file

        except Exception as e:
            print(f"Error loading portfolio: {e}")
            self.portfolio_df = pd.DataFrame(columns=self.columns)
            self.save_portfolio()

    def add_stock(self, stock_data):
        """Add stock to portfolio"""
        print("Starting add_stock with data:", stock_data)  # Debug print
        
        try:
            # Validate the incoming data
            validated_data = self._validate_stock_data(stock_data, 'buy')
            
            # Get current price and other info first
            stock_info = self.stock_service.get_stock_info(validated_data['symbol'])
            current_price = stock_info['price']
            
            # Create a complete position data dictionary
            position_data = {
                'symbol': validated_data['symbol'],
                'quantity': validated_data['quantity'],
                'price': validated_data['price'],
                'current_price': current_price,
                'sector': stock_info.get('sector', 'Unknown'),
                'industry': stock_info.get('industry', 'Unknown'),
                'percent_change': ((current_price - validated_data['price']) / validated_data['price']) * 100,
                'position_type': 'long',
                'position_value': validated_data['quantity'] * current_price
            }

            # First, check if we have any existing positions
            if self.portfolio_df.empty:
                # If DataFrame is empty, create first position
                self.portfolio_df = pd.DataFrame([position_data])
            else:
                # Check for existing position
                mask = (self.portfolio_df['symbol'] == validated_data['symbol']) & (self.portfolio_df['position_type'] == 'long')
                
                if mask.any():
                    # Update existing position
                    idx = self.portfolio_df[mask].index[0]
                    current_quantity = self.portfolio_df.at[idx, 'quantity']
                    current_price_avg = self.portfolio_df.at[idx, 'price']
                    
                    # Calculate new average price
                    total_value = (current_quantity * current_price_avg) + (validated_data['quantity'] * validated_data['price'])
                    new_quantity = current_quantity + validated_data['quantity']
                    new_price = total_value / new_quantity
                    
                    # Update all fields
                    update_data = {
                        'quantity': new_quantity,
                        'price': new_price,
                        'current_price': current_price,
                        'percent_change': ((current_price - new_price) / new_price) * 100,
                        'position_value': new_quantity * current_price
                    }
                    
                    for key, value in update_data.items():
                        self.portfolio_df.at[idx, key] = value
                else:
                    # Add new position
                    new_position = pd.DataFrame([position_data])
                    self.portfolio_df = pd.concat([self.portfolio_df, new_position], ignore_index=True)

            # Create and add transaction record
            transaction = {
                "type": "buy",
                "symbol": validated_data['symbol'],
                "quantity": validated_data['quantity'],
                "price": validated_data['price'],
                "date": validated_data['date']
            }
            self.transactions.append(transaction)
            
            # Update metadata and save
            self.update_portfolio_metadata()
            self.save_portfolio()
            
            print("Stock added successfully")
            return True

        except Exception as e:
            print(f"Error in add_stock: {str(e)}")
            raise

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

    def _validate_stock_data(self, stock_data, transaction_type='buy'):
        """Validate stock data based on transaction type"""
        print(f"Starting validation for {transaction_type} with data:", stock_data)  # Debug print
        
        # Define field mappings for each transaction type
        field_mappings = {
            'buy': {
                'symbol': 'stockSymbol',
                'quantity': 'stockPurchaseQuantity',
                'price': 'stockPurchasePrice',
                'date': 'stockPurchaseDate'
            },
            'sell': {
                'symbol': 'stockSymbol',
                'quantity': 'stockSellQuantity',
                'price': 'stockSellPrice',
                'date': 'stockSellDate'
            },
            'short': {
                'symbol': 'stockSymbol',
                'quantity': 'stockShortQuantity',
                'price': 'stockShortPrice',
                'date': 'stockShortDate'
            },
            'cover': {
                'symbol': 'stockSymbol',
                'quantity': 'stockCoverQuantity',
                'price': 'stockCoverPrice',
                'date': 'stockCoverDate'
            }
        }

        if transaction_type not in field_mappings:
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        fields = field_mappings[transaction_type]
        
        # First, ensure all required fields exist in stock_data
        missing_fields = [api_name for _, api_name in fields.items() if api_name not in stock_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Then validate each field
        validated_data = {}
        
        # Validate symbol
        symbol = stock_data[fields['symbol']]
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        validated_data['symbol'] = symbol.upper()

        # Validate quantity
        try:
            quantity = float(stock_data[fields['quantity']])
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            validated_data['quantity'] = quantity
        except (TypeError, ValueError):
            raise ValueError(f"Invalid quantity value: {stock_data[fields['quantity']]}")

        # Validate price
        try:
            price = float(stock_data[fields['price']])
            if price <= 0:
                raise ValueError("Price must be positive")
            validated_data['price'] = price
        except (TypeError, ValueError):
            raise ValueError(f"Invalid price value: {stock_data[fields['price']]}")

        # Validate date
        date_str = stock_data[fields['date']]
        try:
            # Validate date format
            datetime.strptime(date_str, '%Y-%m-%d')
            validated_data['date'] = date_str
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        print(f"Validation successful. Validated data:", validated_data)  # Debug print
        return validated_data


    def sell_stock(self, stock_data):
       """Sell stock from portfolio"""
       validated_data = self._validate_stock_data(stock_data, 'sell')
       
       # Find the long position
       mask = (self.portfolio_df['symbol'] == validated_data['symbol']) & (self.portfolio_df['position_type'] == 'long')
       if not mask.any():
           raise ValueError(f"No long position found for {validated_data['symbol']}")

       position = self.portfolio_df[mask].iloc[0]
       if validated_data['quantity'] > position['quantity']:
           raise ValueError(f"Insufficient shares to sell: have {position['quantity']}, trying to sell {validated_data['quantity']}")

       # Calculate realized gain/loss
       realized_gain = (validated_data['price'] - position['price']) * validated_data['quantity']

       # Create transaction record
       transaction = {
           "type": "sell",
           "symbol": validated_data['symbol'],
           "quantity": validated_data['quantity'],
           "price": validated_data['price'],
           "date": validated_data['date'],
           "realized_gain": realized_gain
       }
       self.transactions.append(transaction)

       # Update portfolio
       idx = mask[mask].index[0]
       if validated_data['quantity'] == position['quantity']:
           self.portfolio_df = self.portfolio_df.drop(idx)
       else:
           self.portfolio_df.at[idx, 'quantity'] -= validated_data['quantity']

       # Update metadata
       self.metadata["total_realized_gains"] += realized_gain
       self.update_portfolio_metadata()
       self.save_portfolio()

       return {
           "realized_gain": realized_gain,
           "remaining_shares": position['quantity'] - validated_data['quantity'],
           "running_total": self.get_running_total(validated_data['symbol'])
       }

    def add_short_position(self, stock_data):
       """Add short position to portfolio"""
       validated_data = self._validate_stock_data(stock_data, 'short')
       
       # Create transaction record
       transaction = {
           "type": "short",
           "symbol": validated_data['symbol'],
           "quantity": validated_data['quantity'],
           "price": validated_data['price'],
           "date": validated_data['date']
       }
       self.transactions.append(transaction)

       # Get current price and other info
       try:
           stock_info = self.stock_service.get_stock_info(validated_data['symbol'])
           validated_data.update({
               "current_price": stock_info['price'],
               "sector": stock_info.get('sector', 'Unknown'),
               "industry": stock_info.get('industry', 'Unknown')
           })
       except Exception as e:
           raise ValueError(f"Error fetching stock info: {str(e)}")

       # Calculate percent change (for shorts, positive change in stock price is negative for position)
       percent_change = ((validated_data['price'] - validated_data['current_price']) / validated_data['price']) * 100

       # Update portfolio
       mask = (self.portfolio_df['symbol'] == validated_data['symbol']) & (self.portfolio_df['position_type'] == 'short')
       if mask.any():
           # Update existing short position
           idx = self.portfolio_df[mask].index[0]
           current_quantity = self.portfolio_df.at[idx, 'quantity']
           current_price = self.portfolio_df.at[idx, 'price']
           
           # Calculate new average price
           total_value = (current_quantity * current_price) + (validated_data['quantity'] * validated_data['price'])
           new_quantity = current_quantity + validated_data['quantity']
           new_price = total_value / new_quantity
           
           self.portfolio_df.at[idx, 'quantity'] = new_quantity
           self.portfolio_df.at[idx, 'price'] = new_price
           self.portfolio_df.at[idx, 'current_price'] = validated_data['current_price']
           self.portfolio_df.at[idx, 'percent_change'] = percent_change
       else:
           # Add new short position
           new_position = pd.DataFrame([{
               'symbol': validated_data['symbol'],
               'quantity': validated_data['quantity'],
               'price': validated_data['price'],
               'current_price': validated_data['current_price'],
               'sector': validated_data['sector'],
               'industry': validated_data['industry'],
               'percent_change': percent_change,
               'position_type': 'short'
           }])
           self.portfolio_df = pd.concat([self.portfolio_df, new_position], ignore_index=True)

       self.update_portfolio_metadata()
       self.save_portfolio()

    def cover_short(self, stock_data):
       """Cover short position"""
       validated_data = self._validate_stock_data(stock_data, 'cover')
       
       # Find the short position
       mask = (self.portfolio_df['symbol'] == validated_data['symbol']) & (self.portfolio_df['position_type'] == 'short')
       if not mask.any():
           raise ValueError(f"No short position found for {validated_data['symbol']}")

       position = self.portfolio_df[mask].iloc[0]
       if validated_data['quantity'] > position['quantity']:
           raise ValueError(f"Insufficient shares to cover: have {position['quantity']}, trying to cover {validated_data['quantity']}")

       # Calculate realized gain/loss (for shorts, gain is original price - cover price)
       realized_gain = (position['price'] - validated_data['price']) * validated_data['quantity']

       # Create transaction record
       transaction = {
           "type": "cover",
           "symbol": validated_data['symbol'],
           "quantity": validated_data['quantity'],
           "price": validated_data['price'],
           "date": validated_data['date'],
           "realized_gain": realized_gain
       }
       self.transactions.append(transaction)

       # Update portfolio
       idx = mask[mask].index[0]
       if validated_data['quantity'] == position['quantity']:
           self.portfolio_df = self.portfolio_df.drop(idx)
       else:
           self.portfolio_df.at[idx, 'quantity'] -= validated_data['quantity']

       # Update metadata
       self.metadata["total_realized_gains"] += realized_gain
       self.update_portfolio_metadata()
       self.save_portfolio()

       return {
           "realized_gain": realized_gain,
           "remaining_shares": position['quantity'] - validated_data['quantity'],
           "running_total": self.get_running_total(validated_data['symbol'])
       }
   
    def update_stock_prices(self):
        """Update current prices for all stocks"""
        if self.portfolio_df.empty:
            return
            
        symbols = self.portfolio_df['symbol'].unique().tolist()
        try:
            for symbol in symbols:
                stock_info = self.stock_service.get_stock_info(symbol)
                current_price = stock_info['price']
                
                # Update all positions for this symbol
                mask = self.portfolio_df['symbol'] == symbol
                self.portfolio_df.loc[mask, 'current_price'] = current_price
                
                # Calculate percent change based on position type
                self.portfolio_df.loc[mask, 'percent_change'] = self.portfolio_df[mask].apply(
                    lambda row: ((current_price - row['price']) / row['price'] * 100) * 
                            (-1 if row['position_type'] == 'short' else 1),
                    axis=1
                )
                
            self.update_portfolio_metadata()
            self.save_portfolio()
    
        except Exception as e:
            print(f"Error updating prices: {str(e)}")
            raise ValueError(f"Failed to update prices: {str(e)}")
       
    def update_portfolio_metadata(self):
       """Update portfolio metadata"""
       if not self.portfolio_df.empty:
           # Calculate position values (negative for shorts, positive for longs)
           self.portfolio_df['position_value'] = self.portfolio_df.apply(
               lambda row: row['quantity'] * row['current_price'] * 
               (-1 if row['position_type'] == 'short' else 1),
               axis=1
           )
           
           # Update total portfolio value
           self.metadata["total_value"] = self.portfolio_df['position_value'].sum()
           
           # Calculate sector allocations
           if self.metadata["total_value"] != 0:
               sector_values = self.portfolio_df.groupby('sector')['position_value'].sum()
               self.metadata["sectors"] = {
                   sector: (value / abs(self.metadata["total_value"]) * 100)
                   for sector, value in sector_values.items()
               }
           else:
               self.metadata["sectors"] = {}
       else:
           self.metadata["total_value"] = 0
           self.metadata["sectors"] = {}
       
       self.metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_running_total(self, symbol):
       """Get running total of realized gains/losses for a symbol"""
       total = 0
       # Get all transactions for this symbol
       symbol_transactions = [t for t in self.transactions if t['symbol'] == symbol]
       
       # Calculate running total
       for transaction in symbol_transactions:
           if transaction['type'] in ['sell', 'cover'] and 'realized_gain' in transaction:
               total += transaction['realized_gain']
       
       return total

    def calculate_cost_basis(self, symbol, position_type='long'):
       """Calculate the average cost basis for a symbol and position type"""
       mask = (self.portfolio_df['symbol'] == symbol) & (self.portfolio_df['position_type'] == position_type)
       if not mask.any():
           return 0
       
       position = self.portfolio_df.loc[mask].iloc[0]
       return position['price']

    def get_portfolio_summary(self):
       """Get a summary of the portfolio including all positions and metadata"""
       if self.portfolio_df.empty:
           return {
               "positions": [],
               "metadata": self.metadata
           }

       positions = []
       for _, row in self.portfolio_df.iterrows():
           position = {
               "symbol": row['symbol'],
               "quantity": row['quantity'],
               "price": row['price'],
               "current_price": row['current_price'],
               "position_type": row['position_type'],
               "sector": row['sector'],
               "industry": row['industry'],
               "percent_change": row['percent_change'],
               "market_value": abs(row['quantity'] * row['current_price']),
               "unrealized_gain": (row['current_price'] - row['price']) * row['quantity'] * 
                                (-1 if row['position_type'] == 'short' else 1),
               "running_total_gains": self.get_running_total(row['symbol'])
           }
           positions.append(position)

       return {
           "positions": positions,
           "metadata": self.metadata
       }

    def validate_position_exists(self, symbol, position_type):
       """Validate that a position exists for the given symbol and type"""
       mask = (self.portfolio_df['symbol'] == symbol) & (self.portfolio_df['position_type'] == position_type)
       if not mask.any():
           raise ValueError(f"No {position_type} position found for {symbol}")
       return self.portfolio_df.loc[mask].iloc[0]

    def get_position_type_count(self):
       """Get count of long and short positions"""
       if self.portfolio_df.empty:
           return {"long": 0, "short": 0}
           
       position_counts = self.portfolio_df['position_type'].value_counts()
       return {
           "long": position_counts.get('long', 0),
           "short": position_counts.get('short', 0)
       }

    def get_sector_exposure(self):
       """Calculate sector exposure for both long and short positions"""
       if self.portfolio_df.empty:
           return {"long": {}, "short": {}}

       sector_exposure = {"long": {}, "short": {}}
       
       for position_type in ['long', 'short']:
           mask = self.portfolio_df['position_type'] == position_type
           if not mask.any():
               continue
               
           positions = self.portfolio_df[mask]
           total_value = abs(positions['position_value'].sum())
           
           if total_value > 0:
               sector_values = positions.groupby('sector')['position_value'].sum()
               sector_exposure[position_type] = {
                   sector: (abs(value) / total_value * 100)
                   for sector, value in sector_values.items()
               }

       return sector_exposure