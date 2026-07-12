from strategies import StrategyFactory
from logger import get_logger

logger = get_logger(__name__)

class RiskManager:
    """Risk management module"""
    
    def __init__(self, account_balance, max_loss_percent=2, max_position_size=0.1):
        self.account_balance = account_balance
        self.max_loss_percent = max_loss_percent
        self.max_position_size = max_position_size
        self.open_positions = {}
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calculate position size based on risk management rules"""
        try:
            risk_amount = self.account_balance * (self.max_loss_percent / 100)
            price_difference = entry_price - stop_loss_price
            
            if price_difference <= 0:
                logger.warning("Invalid stop loss price")
                return 0
            
            position_size = risk_amount / price_difference
            max_position = self.account_balance * self.max_position_size / entry_price
            
            return min(position_size, max_position)
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def calculate_stop_loss(self, entry_price, stop_loss_percent):
        """Calculate stop loss price"""
        return entry_price * (1 - stop_loss_percent / 100)
    
    def calculate_take_profit(self, entry_price, take_profit_percent):
        """Calculate take profit price"""
        return entry_price * (1 + take_profit_percent / 100)
    
    def update_balance(self, amount):
        """Update account balance"""
        self.account_balance += amount
        logger.info(f"Account balance updated: ${self.account_balance}")
    
    def add_position(self, symbol, entry_price, quantity, stop_loss, take_profit):
        """Track an open position"""
        self.open_positions[symbol] = {
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'unrealized_pl': 0
        }
    
    def remove_position(self, symbol):
        """Remove closed position"""
        if symbol in self.open_positions:
            del self.open_positions[symbol]
    
    def update_position_pl(self, symbol, current_price):
        """Update unrealized P&L"""
        if symbol in self.open_positions:
            pos = self.open_positions[symbol]
            pl = (current_price - pos['entry_price']) * pos['quantity']
            pos['unrealized_pl'] = pl
            return pl
        return 0
    
    def get_total_unrealized_pl(self):
        """Get total unrealized P&L across all positions"""
        return sum(pos['unrealized_pl'] for pos in self.open_positions.values())
