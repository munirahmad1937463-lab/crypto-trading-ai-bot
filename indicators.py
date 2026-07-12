import numpy as np
import pandas as pd
from logger import get_logger

logger = get_logger(__name__)

class TechnicalIndicators:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index (RSI)"""
        try:
            deltas = np.diff(prices)
            seed = deltas[:period+1]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down if down != 0 else 0
            rsi = np.zeros_like(prices, dtype=float)
            rsi[:period] = 100. - 100. / (1. + rs)
            
            for i in range(period, len(prices)):
                delta = deltas[i-1]
                if delta > 0:
                    upval = delta
                    downval = 0.
                else:
                    upval = 0.
                    downval = -delta
                
                up = (up * (period - 1) + upval) / period
                down = (down * (period - 1) + downval) / period
                rs = up / down if down != 0 else 0
                rsi[i] = 100. - 100. / (1. + rs)
            
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            ema_fast = pd.Series(prices).ewm(span=fast).mean().values
            ema_slow = pd.Series(prices).ewm(span=slow).mean().values
            macd = ema_fast - ema_slow
            macd_signal = pd.Series(macd).ewm(span=signal).mean().values
            macd_hist = macd - macd_signal
            return macd, macd_signal, macd_hist
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None, None, None
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        try:
            sma = pd.Series(prices).rolling(window=period).mean().values
            std = pd.Series(prices).rolling(window=period).std().values
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            return upper_band, sma, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return None, None, None
    
    @staticmethod
    def calculate_sma(prices, period):
        """Calculate Simple Moving Average"""
        try:
            return pd.Series(prices).rolling(window=period).mean().values
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return None
    
    @staticmethod
    def calculate_ema(prices, period):
        """Calculate Exponential Moving Average"""
        try:
            return pd.Series(prices).ewm(span=period).mean().values
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return None
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Calculate Average True Range"""
        try:
            tr1 = high - low
            tr2 = np.abs(high - np.roll(close, 1))
            tr3 = np.abs(low - np.roll(close, 1))
            tr = np.maximum(tr1, tr2, tr3)
            atr = pd.Series(tr).rolling(window=period).mean().values
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return None
    
    @staticmethod
    def calculate_stochastic(high, low, close, period=14, smooth_k=3, smooth_d=3):
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = pd.Series(low).rolling(window=period).min().values
            highest_high = pd.Series(high).rolling(window=period).max().values
            
            k = 100 * (close - lowest_low) / (highest_high - lowest_low)
            k_smooth = pd.Series(k).rolling(window=smooth_k).mean().values
            d_smooth = pd.Series(k_smooth).rolling(window=smooth_d).mean().values
            
            return k_smooth, d_smooth
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return None, None
    
    @staticmethod
    def calculate_volume_sma(volume, period=20):
        """Calculate Volume Simple Moving Average"""
        try:
            return pd.Series(volume).rolling(window=period).mean().values
        except Exception as e:
            logger.error(f"Error calculating Volume SMA: {e}")
            return None
    
    @staticmethod
    def prepare_dataframe(ohlcv_data):
        """Prepare OHLCV data as DataFrame with indicators"""
        try:
            df = pd.DataFrame(ohlcv_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            # Add indicators
            df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'].values)
            df['sma_20'] = TechnicalIndicators.calculate_sma(df['close'].values, 20)
            df['sma_50'] = TechnicalIndicators.calculate_sma(df['close'].values, 50)
            df['ema_12'] = TechnicalIndicators.calculate_ema(df['close'].values, 12)
            df['ema_26'] = TechnicalIndicators.calculate_ema(df['close'].values, 26)
            
            macd, macd_signal, macd_hist = TechnicalIndicators.calculate_macd(df['close'].values)
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_hist'] = macd_hist
            
            upper_bb, middle_bb, lower_bb = TechnicalIndicators.calculate_bollinger_bands(df['close'].values)
            df['bb_upper'] = upper_bb
            df['bb_middle'] = middle_bb
            df['bb_lower'] = lower_bb
            
            df['atr'] = TechnicalIndicators.calculate_atr(df['high'].values, df['low'].values, df['close'].values)
            
            return df
        except Exception as e:
            logger.error(f"Error preparing DataFrame: {e}")
            return None
