import time
import json
from datetime import datetime
from exchange_connector import ExchangeConnector
from indicators import TechnicalIndicators
from strategies import StrategyFactory
from risk_manager import RiskManager
from logger import get_logger
from config import (
    EXCHANGE_NAME, EXCHANGE_API_KEY, EXCHANGE_API_SECRET, EXCHANGE_SANDBOX,
    TRADING_SYMBOLS, TIMEFRAME, CHECK_INTERVAL,
    MAX_LOSS_PERCENT, MAX_POSITION_SIZE, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT
)

logger = get_logger(__name__)

class CryptoTradingBot:
    """Main crypto trading bot"""
    
    def __init__(self, strategy_name='rsi_macd'):
        self.exchange = ExchangeConnector(
            EXCHANGE_NAME, 
            EXCHANGE_API_KEY, 
            EXCHANGE_API_SECRET,
            sandbox=EXCHANGE_SANDBOX
        )
        
        self.strategy = StrategyFactory.create(strategy_name)
        if not self.strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Initialize risk manager with default balance
        balance_data = self.exchange.fetch_balance()
        total_balance = balance_data.get('total', {}).get('USDT', 1000) if balance_data else 1000
        
        self.risk_manager = RiskManager(
            total_balance,
            max_loss_percent=MAX_LOSS_PERCENT,
            max_position_size=MAX_POSITION_SIZE
        )
        
        self.trades_log = []
        self.is_running = False
        
        logger.info(f"Bot initialized with strategy: {strategy_name}")
        logger.info(f"Account balance: ${self.risk_manager.account_balance}")
    
    def fetch_and_analyze(self, symbol):
        """Fetch market data and generate trading signal"""
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=100)
            if not ohlcv:
                logger.warning(f"No OHLCV data for {symbol}")
                return None
            
            # Prepare dataframe with indicators
            df = TechnicalIndicators.prepare_dataframe(ohlcv)
            if df is None:
                logger.warning(f"Failed to prepare dataframe for {symbol}")
                return None
            
            # Generate signal
            signal = self.strategy.generate_signal(df)
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last'] if ticker else df.iloc[-1]['close']
            
            return {
                'symbol': symbol,
                'price': current_price,
                'signal': signal,
                'df': df,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def execute_buy_order(self, analysis):
        """Execute buy order with risk management"""
        try:
            symbol = analysis['symbol']
            price = analysis['price']
            signal_strength = analysis['signal']['strength']
            
            # Calculate stop loss and take profit
            stop_loss_price = self.risk_manager.calculate_stop_loss(price, STOP_LOSS_PERCENT)
            take_profit_price = self.risk_manager.calculate_take_profit(price, TAKE_PROFIT_PERCENT)
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(price, stop_loss_price)
            
            if position_size <= 0:
                logger.warning(f"Invalid position size for {symbol}: {position_size}")
                return None
            
            # Adjust position size based on signal strength
            adjusted_size = position_size * signal_strength
            
            logger.info(f"Executing BUY order: {symbol}")
            logger.info(f"  Price: ${price}")
            logger.info(f"  Quantity: {adjusted_size}")
            logger.info(f"  Stop Loss: ${stop_loss_price}")
            logger.info(f"  Take Profit: ${take_profit_price}")
            
            # Execute order (set to True to actually trade)
            if False:  # Change to True to enable real trading
                order = self.exchange.create_market_buy_order(symbol, adjusted_size)
                
                if order:
                    self.risk_manager.add_position(
                        symbol, price, adjusted_size, stop_loss_price, take_profit_price
                    )
                    
                    trade_log = {
                        'type': 'BUY',
                        'symbol': symbol,
                        'price': price,
                        'quantity': adjusted_size,
                        'timestamp': datetime.now(),
                        'order_id': order.get('id')
                    }
                    self.trades_log.append(trade_log)
                    logger.info(f"Buy order executed: {order.get('id')}")
                    return order
            else:
                logger.info("Paper trading mode - order not executed")
                return None
        
        except Exception as e:
            logger.error(f"Error executing buy order: {e}")
            return None
    
    def execute_sell_order(self, symbol, price, signal_strength):
        """Execute sell order"""
        try:
            # Check if we have open position
            if symbol not in self.risk_manager.open_positions:
                logger.info(f"No open position for {symbol}")
                return None
            
            position = self.risk_manager.open_positions[symbol]
            quantity = position['quantity']
            
            logger.info(f"Executing SELL order: {symbol}")
            logger.info(f"  Price: ${price}")
            logger.info(f"  Quantity: {quantity}")
            
            # Execute order (set to True to actually trade)
            if False:  # Change to True to enable real trading
                order = self.exchange.create_market_sell_order(symbol, quantity)
                
                if order:
                    # Calculate P&L
                    entry_price = position['entry_price']
                    pnl = (price - entry_price) * quantity
                    pnl_percent = (pnl / (entry_price * quantity)) * 100
                    
                    logger.info(f"Sell order executed: {order.get('id')}")
                    logger.info(f"  Entry Price: ${entry_price}")
                    logger.info(f"  Exit Price: ${price}")
                    logger.info(f"  P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
                    
                    self.risk_manager.remove_position(symbol)
                    self.risk_manager.update_balance(pnl)
                    
                    trade_log = {
                        'type': 'SELL',
                        'symbol': symbol,
                        'price': price,
                        'quantity': quantity,
                        'entry_price': entry_price,
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'timestamp': datetime.now(),
                        'order_id': order.get('id')
                    }
                    self.trades_log.append(trade_log)
                    return order
            else:
                logger.info("Paper trading mode - order not executed")
                return None
        
        except Exception as e:
            logger.error(f"Error executing sell order: {e}")
            return None
    
    def check_position_levels(self, symbol, current_price):
        """Check if position hit stop loss or take profit"""
        if symbol not in self.risk_manager.open_positions:
            return None
        
        position = self.risk_manager.open_positions[symbol]
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']
        
        if current_price <= stop_loss:
            logger.warning(f"Stop loss hit for {symbol} at ${current_price}")
            return 'STOP_LOSS'
        
        if current_price >= take_profit:
            logger.info(f"Take profit hit for {symbol} at ${current_price}")
            return 'TAKE_PROFIT'
        
        return None
    
    def run_once(self):
        """Run bot for one cycle"""
        try:
            logger.info("=" * 50)
            logger.info(f"Bot cycle started at {datetime.now()}")
            logger.info(f"Strategy: {self.strategy.name}")
            logger.info(f"Account Balance: ${self.risk_manager.account_balance:.2f}")
            logger.info(f"Open Positions: {len(self.risk_manager.open_positions)}")
            
            for symbol in TRADING_SYMBOLS:
                try:
                    # Analyze market
                    analysis = self.fetch_and_analyze(symbol)
                    if not analysis:
                        continue
                    
                    signal_action = analysis['signal']['action']
                    signal_strength = analysis['signal']['strength']
                    current_price = analysis['price']
                    
                    logger.info(f"\n{symbol}:")
                    logger.info(f"  Price: ${current_price:.4f}")
                    logger.info(f"  Signal: {signal_action.upper()} (strength: {signal_strength:.2f})")
                    
                    # Check position levels
                    level_check = self.check_position_levels(symbol, current_price)
                    if level_check:
                        self.execute_sell_order(symbol, current_price, 1.0)
                    
                    # Execute trades based on signal
                    if signal_action == 'buy' and signal_strength > 0.5:
                        self.execute_buy_order(analysis)
                    
                    elif signal_action == 'sell' and signal_strength > 0.5:
                        self.execute_sell_order(symbol, current_price, signal_strength)
                    
                    # Update position P&L
                    if symbol in self.risk_manager.open_positions:
                        unrealized_pl = self.risk_manager.update_position_pl(symbol, current_price)
                        logger.info(f"  Unrealized P&L: ${unrealized_pl:.2f}")
                
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
            
            total_pl = self.risk_manager.get_total_unrealized_pl()
            logger.info(f"\nTotal Unrealized P&L: ${total_pl:.2f}")
            logger.info("=" * 50)
        
        except Exception as e:
            logger.error(f"Error in bot cycle: {e}")
    
    def run(self):
        """Run bot continuously"""
        self.is_running = True
        logger.info("Bot started")
        
        try:
            while self.is_running:
                self.run_once()
                logger.info(f"Next check in {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        logger.info("Bot stopped")
        self.save_trades_log()
    
    def save_trades_log(self):
        """Save trades log to file"""
        try:
            with open('trades_log.json', 'w') as f:
                json.dump(self.trades_log, f, indent=2, default=str)
            logger.info(f"Trades log saved: {len(self.trades_log)} trades")
        except Exception as e:
            logger.error(f"Error saving trades log: {e}")


if __name__ == '__main__':
    try:
        bot = CryptoTradingBot(strategy_name='rsi_macd')
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
