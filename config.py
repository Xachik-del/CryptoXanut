# config.py

# Торговые пары для фьючерсов
SYMBOLS = [
    "BTC/USDT:USDT",  # Формат Binance Futures
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    "BNB/USDT:USDT",
    "DOGE/USDT:USDT",
    "XRP/USDT:USDT",  # Ripple
    "ADA/USDT:USDT",  # Cardano
    "AVAX/USDT:USDT", # Avalanche
    "MATIC/USDT:USDT", # Polygon
    "LINK/USDT:USDT"  # Chainlink
]

# Настройки Telegram
TELEGRAM_TOKEN = "7910233528:AAF9RuaSa_UyxFmgLlAC9REDtG9OfJOHOFE"
TELEGRAM_CHAT_ID = "705512639"

# API ключи Binance
BINANCE_API_KEY = "65PXvD8ddnf8efNpy7tc4H5LmBpPIttCOSH8AVGIOyXzfxIHcnUT5duhlnjbVw0d"
BINANCE_API_SECRET = "rKgV2Cxpg6Ga6XKYpub98SbAyg0rMw1QA61DJPQDG09hiHSJgc9UwqSqnqwXkkCf"

# Таймфреймы для фьючерсной торговли
TIMEFRAME = "1m"  # 1-минутный таймфрейм для краткосрочной торговли
FUTURES_INTERVAL = 30  # Проверка каждые 30 секунд

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
