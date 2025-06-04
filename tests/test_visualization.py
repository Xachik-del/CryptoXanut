import ccxt
import pandas as pd
from datetime import datetime, timedelta
from indicators import add_indicators
from visualizer import plot_chart, plot_signal
from config import TIMEFRAME, SYMBOLS
import os
import subprocess

def fetch_test_data(symbol, timeframe='1m', limit=100):
    """Получение тестовых данных с биржи"""
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    # Получение OHLCV данных
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    # Создание DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    return df

def open_image(image_path):
    """Открытие изображения в системе по умолчанию"""
    abs_path = os.path.abspath(image_path)
    print(f"Открываю файл: {abs_path}")
    if os.path.exists(abs_path):
        if os.name == 'nt':  # Windows
            os.startfile(abs_path)
        elif os.name == 'posix':  # Linux/Mac
            subprocess.run(['xdg-open', abs_path])
    else:
        print(f"Файл не найден: {abs_path}")


def main():
    # Выбор тестовой пары (BTC/USDT)
    symbol = SYMBOLS[0]
    
    print(f"Получение данных для {symbol}...")
    df = fetch_test_data(symbol, TIMEFRAME)
    
    print("Добавление индикаторов...")
    df = add_indicators(df)
    
    print("Создание графика с индикаторами...")
    chart_filename = plot_chart(df, symbol, TIMEFRAME)
    
    print("Создание графика с тестовым сигналом...")
    last_price = df['close'].iloc[-1]
    signal_filename = plot_signal(
        df, 
        symbol, 
        TIMEFRAME,
        "ПОКУПКА",
        last_price,
        last_price * 0.98,  # -2% для стоп-лосса
        last_price * 1.06   # +6% для тейк-профита
    )
    
    print("\nГрафики сохранены в директории 'charts'")
    print(f"Последняя цена {symbol}: {last_price:.2f}")
    
    # Открытие графиков
    print("\nОткрытие графиков...")
    open_image(chart_filename)
    open_image(signal_filename)

if __name__ == "__main__":
    main() 