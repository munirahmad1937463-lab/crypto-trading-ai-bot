import os
from dotenv import load_dotenv

load_dotenv()

# Exchange Settings
EXCHANGE_NAME = os.getenv('EXCHANGE_NAME', 'binance')
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY', '')
EXCHANGE_API_SECRET = os.getenv('EXCHANGE_API_SECRET', '')
EXCHANGE_SANDBOX = os.getenv('EXCHANGE_SANDBOX', 'true').lower() == 'true'

# Trading Settings
TRADING_SYMBOLS = os.getenv('TRADING_SYMBOLS', 'BTC/USDT,ETH/USDT').split(',')
TIMEFRAME = os.getenv('TIMEFRAME', '1h')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

# Risk Management
MAX_LOSS_PERCENT = float(os.getenv('MAX_LOSS_PERCENT', '2'))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.1'))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '5'))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '10'))

# AI Model
USE_ML_MODEL = os.getenv('USE_ML_MODEL', 'true').lower() == 'true'
MODEL_TYPE = os.getenv('MODEL_TYPE', 'random_forest')
TRAIN_DATA_DAYS = int(os.getenv('TRAIN_DATA_DAYS', '365'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')

# Notifications
ENABLE_DISCORD = os.getenv('ENABLE_DISCORD', 'false').lower() == 'true'
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM', 'false').lower() == 'true'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
