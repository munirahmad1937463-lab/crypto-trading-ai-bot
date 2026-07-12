import ccxt
import time
from logger import get_logger

logger = get_logger(__name__)

class ExchangeConnector:
    """Unified exchange connector using CCXT"""
    
    def __init__(self, exchange_name, api_key, api_secret, sandbox=False):
        self.exchange_name = exchange_name
        
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'sandbox': sandbox
        })
        
        logger.info(f"Connected to {exchange_name} exchange")
    
    def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        """Fetch candlestick data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            logger.debug(f"Fetched {len(ohlcv)} candles for {symbol}")
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None
    
    def fetch_ticker(self, symbol):
        """Fetch current ticker data"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def fetch_balance(self):
        """Fetch account balance"""
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None
    
    def create_market_buy_order(self, symbol, amount):
        """Create market buy order"""
        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            logger.info(f"Buy order created: {symbol} x {amount}")
            return order
        except Exception as e:
            logger.error(f"Error creating buy order: {e}")
            return None
    
    def create_market_sell_order(self, symbol, amount):
        """Create market sell order"""
        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            logger.info(f"Sell order created: {symbol} x {amount}")
            return order
        except Exception as e:
            logger.error(f"Error creating sell order: {e}")
            return None
    
    def create_limit_buy_order(self, symbol, amount, price):
        """Create limit buy order"""
        try:
            order = self.exchange.create_limit_buy_order(symbol, amount, price)
            logger.info(f"Limit buy order created: {symbol} x {amount} @ {price}")
            return order
        except Exception as e:
            logger.error(f"Error creating limit buy order: {e}")
            return None
    
    def create_limit_sell_order(self, symbol, amount, price):
        """Create limit sell order"""
        try:
            order = self.exchange.create_limit_sell_order(symbol, amount, price)
            logger.info(f"Limit sell order created: {symbol} x {amount} @ {price}")
            return order
        except Exception as e:
            logger.error(f"Error creating limit sell order: {e}")
            return None
    
    def cancel_order(self, symbol, order_id):
        """Cancel an order"""
        try:
            order = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return order
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return None
    
    def fetch_order(self, symbol, order_id):
        """Fetch order details"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order: {e}")
            return None
    
    def fetch_open_orders(self, symbol=None):
        """Fetch open orders"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return None
    
    def fetch_closed_orders(self, symbol=None, limit=50):
        """Fetch closed orders"""
        try:
            orders = self.exchange.fetch_closed_orders(symbol, limit=limit)
            return orders
        except Exception as e:
            logger.error(f"Error fetching closed orders: {e}")
            return None
