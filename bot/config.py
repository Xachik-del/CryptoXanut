# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Торговые пары для фьючерсов
SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "DOGE/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "MATIC/USDT",
    "LINK/USDT"
]

# Настройки Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# API ключи Binance
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Таймфреймы для фьючерсной торговли
TIMEFRAME = "5m"  # 1-минутный таймфрейм для краткосрочной торговли
FUTURES_INTERVAL = 60  # Проверка каждые 30 секунд

# Параметры торговли
LEVERAGE = 5  # Плечо по умолчанию
POSITION_SIZE = 0.1  # Размер позиции как доля от доступной маржи
STOP_LOSS_PCT = 0.02  # 2% стоп-лосс
TAKE_PROFIT_PCT = 0.06  # 6% тейк-профит

# Параметры технического анализа
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80
ADX_THRESHOLD = 25  # Минимальный ADX для силы тренда
VOLUME_THRESHOLD = 1.5  # Порог всплеска объема
