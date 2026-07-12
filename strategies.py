from abc import ABC, abstractmethod
from indicators import TechnicalIndicators
from logger import get_logger

logger = get_logger(__name__)

class BaseTradingStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, name):
        self.name = name
        self.signals_history = []
    
    @abstractmethod
    def generate_signal(self, df):
        """Generate buy/sell signal"""
        pass
    
    def log_signal(self, symbol, signal):
        self.signals_history.append({
            'symbol': symbol,
            'signal': signal
        })


class RSIMACDStrategy(BaseTradingStrategy):
    """RSI + MACD combined strategy"""
    
    def __init__(self, rsi_threshold_buy=30, rsi_threshold_sell=70, 
                 macd_threshold=0):
        super().__init__('RSI_MACD')
        self.rsi_threshold_buy = rsi_threshold_buy
        self.rsi_threshold_sell = rsi_threshold_sell
        self.macd_threshold = macd_threshold
    
    def generate_signal(self, df):
        """
        Generate signal based on RSI and MACD
        Returns: {'action': 'buy'/'sell'/'hold', 'strength': 0-1}
        """
        try:
            if df is None or len(df) < 26:
                return {'action': 'hold', 'strength': 0}
            
            latest = df.iloc[-1]
            
            # RSI Signal
            rsi = latest['rsi']
            if rsi < self.rsi_threshold_buy:
                rsi_signal = 'buy'
                rsi_strength = 1 - (rsi / self.rsi_threshold_buy)
            elif rsi > self.rsi_threshold_sell:
                rsi_signal = 'sell'
                rsi_strength = (rsi - self.rsi_threshold_sell) / (100 - self.rsi_threshold_sell)
            else:
                rsi_signal = 'hold'
                rsi_strength = 0
            
            # MACD Signal
            macd_hist = latest['macd_hist']
            if macd_hist > self.macd_threshold:
                macd_signal = 'buy'
                macd_strength = min(abs(macd_hist) / 0.001, 1)
            elif macd_hist < -self.macd_threshold:
                macd_signal = 'sell'
                macd_strength = min(abs(macd_hist) / 0.001, 1)
            else:
                macd_signal = 'hold'
                macd_strength = 0
            
            # Combine signals
            if rsi_signal == macd_signal and rsi_signal != 'hold':
                action = rsi_signal
                strength = (rsi_strength + macd_strength) / 2
            elif rsi_signal != 'hold':
                action = rsi_signal
                strength = rsi_strength * 0.7
            elif macd_signal != 'hold':
                action = macd_signal
                strength = macd_strength * 0.7
            else:
                action = 'hold'
                strength = 0
            
            return {'action': action, 'strength': strength}
        except Exception as e:
            logger.error(f"Error generating RSI_MACD signal: {e}")
            return {'action': 'hold', 'strength': 0}


class BollingerBandsStrategy(BaseTradingStrategy):
    """Bollinger Bands mean reversion strategy"""
    
    def __init__(self, period=20, std_dev=2):
        super().__init__('BOLLINGER_BANDS')
        self.period = period
        self.std_dev = std_dev
    
    def generate_signal(self, df):
        """
        Generate signal based on Bollinger Bands
        """
        try:
            if df is None or len(df) < self.period:
                return {'action': 'hold', 'strength': 0}
            
            latest = df.iloc[-1]
            
            close = latest['close']
            upper = latest['bb_upper']
            lower = latest['bb_lower']
            middle = latest['bb_middle']
            
            # Check if price touches bands
            if close < lower:
                action = 'buy'
                strength = (lower - close) / (upper - lower)
            elif close > upper:
                action = 'sell'
                strength = (close - upper) / (upper - lower)
            else:
                action = 'hold'
                strength = 0
            
            return {'action': action, 'strength': min(strength, 1)}
        except Exception as e:
            logger.error(f"Error generating Bollinger Bands signal: {e}")
            return {'action': 'hold', 'strength': 0}


class MovingAverageCrossoverStrategy(BaseTradingStrategy):
    """Simple Moving Average Crossover strategy"""
    
    def __init__(self, fast_period=20, slow_period=50):
        super().__init__('MA_CROSSOVER')
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signal(self, df):
        """
        Generate signal based on MA crossover
        """
        try:
            if df is None or len(df) < self.slow_period:
                return {'action': 'hold', 'strength': 0}
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            sma_fast = latest['sma_20']
            sma_slow = latest['sma_50']
            prev_fast = prev['sma_20']
            prev_slow = prev['sma_50']
            
            # Golden cross
            if prev_fast <= prev_slow and sma_fast > sma_slow:
                action = 'buy'
                strength = min(abs(sma_fast - sma_slow) / sma_slow, 1)
            # Death cross
            elif prev_fast >= prev_slow and sma_fast < sma_slow:
                action = 'sell'
                strength = min(abs(sma_fast - sma_slow) / sma_slow, 1)
            else:
                action = 'hold'
                strength = 0
            
            return {'action': action, 'strength': strength}
        except Exception as e:
            logger.error(f"Error generating MA Crossover signal: {e}")
            return {'action': 'hold', 'strength': 0}


class StochasticStrategy(BaseTradingStrategy):
    """Stochastic Oscillator strategy"""
    
    def __init__(self, period=14, overbought=80, oversold=20):
        super().__init__('STOCHASTIC')
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signal(self, df):
        """
        Generate signal based on Stochastic Oscillator
        """
        try:
            if df is None or len(df) < self.period:
                return {'action': 'hold', 'strength': 0}
            
            k_smooth, d_smooth = TechnicalIndicators.calculate_stochastic(
                df['high'].values, 
                df['low'].values, 
                df['close'].values,
                self.period
            )
            
            if k_smooth is None or d_smooth is None:
                return {'action': 'hold', 'strength': 0}
            
            latest_k = k_smooth[-1]
            latest_d = d_smooth[-1]
            
            if latest_k < self.oversold and latest_k > latest_d:
                action = 'buy'
                strength = 1 - (latest_k / self.oversold)
            elif latest_k > self.overbought and latest_k < latest_d:
                action = 'sell'
                strength = (latest_k - self.overbought) / (100 - self.overbought)
            else:
                action = 'hold'
                strength = 0
            
            return {'action': action, 'strength': min(strength, 1)}
        except Exception as e:
            logger.error(f"Error generating Stochastic signal: {e}")
            return {'action': 'hold', 'strength': 0}


class StrategyFactory:
    """Factory for creating trading strategies"""
    
    strategies = {
        'rsi_macd': RSIMACDStrategy,
        'bollinger_bands': BollingerBandsStrategy,
        'ma_crossover': MovingAverageCrossoverStrategy,
        'stochastic': StochasticStrategy,
    }
    
    @classmethod
    def create(cls, strategy_name, **kwargs):
        """Create a strategy by name"""
        if strategy_name not in cls.strategies:
            logger.error(f"Unknown strategy: {strategy_name}")
            return None
        
        strategy_class = cls.strategies[strategy_name]
        return strategy_class(**kwargs)
    
    @classmethod
    def get_available_strategies(cls):
        """Get list of available strategies"""
        return list(cls.strategies.keys())
