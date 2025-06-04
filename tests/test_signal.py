import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from bot.core.strategy import analyze_symbol, add_indicators, generate_signal, analyze_trend, analyze_momentum, analyze_volume
from bot.notifications.notifier import send_telegram_message
from bot.config import TIMEFRAME, SYMBOLS, STOP_LOSS_PCT, TAKE_PROFIT_PCT, RSI_OVERSOLD, RSI_OVERBOUGHT
from bot.visualization.visualizer import plot_signal
import logging
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_data():
    """Создание тестовых данных для проверки сигнала"""
    # Создаем DataFrame с тестовыми данными
    dates = pd.date_range(start=datetime.now() - timedelta(days=1), periods=100, freq='1min')
    
    # Создаем данные, которые гарантированно вызовут сигнал
    base_price = 100
    trend = [base_price - i * 0.5 for i in range(100)]  # Нисходящий тренд для перекупленности
    volatility = [2 * (i % 3 - 1) for i in range(100)]  # Небольшая волатильность
    
    data = {
        'open': [trend[i] + volatility[i] for i in range(100)],
        'high': [trend[i] + volatility[i] + 2 for i in range(100)],
        'low': [trend[i] + volatility[i] - 2 for i in range(100)],
        'close': [trend[i] + volatility[i] + 1 for i in range(100)],
        'volume': [1000 + i * 100 for i in range(100)]  # Растущий объем
    }
    
    df = pd.DataFrame(data, index=dates)
    
    # Добавляем индикаторы вручную для гарантированного сигнала
    df['ema8'] = df['close'].ewm(span=8).mean()
    df['ema13'] = df['close'].ewm(span=13).mean()
    df['ema21'] = df['close'].ewm(span=21).mean()
    
    # Устанавливаем RSI в зону перекупленности для последних 10 свечей
    for i in range(10):
        df.loc[df.index[-(i+1)], 'rsi'] = RSI_OVERBOUGHT + 5
    
    # Устанавливаем тренд объема
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    df['volume_std'] = df['volume'].rolling(window=20).std()
    
    # Устанавливаем ADX для сильного тренда
    df['adx'] = 30  # Выше порога ADX_THRESHOLD (25)
    
    return df

def test_analyze_symbol(symbol, df):
    """Тестовая версия analyze_symbol, использующая готовые данные"""
    try:
        # Добавление индикаторов
        df = add_indicators(df)
        
        # Принудительно выставляем RSI и ADX для последних 10 свечей
        for i in range(10):
            df.loc[df.index[-(i+1)], 'rsi'] = RSI_OVERBOUGHT + 5
            df.loc[df.index[-(i+1)], 'adx'] = 30
        
        # Анализ условий
        trend = analyze_trend(df)
        momentum = analyze_momentum(df)
        volume = analyze_volume(df)
        
        # Логирование условий
        logger.info("\nАнализ условий:")
        logger.info(f"Тренд EMA: {trend['ema_trend']}")
        logger.info(f"RSI: {momentum['rsi']:.2f} (Сигнал: {momentum['rsi_signal']})")
        logger.info(f"Тренд объема: {volume['volume_trend']}")
        logger.info(f"Сила тренда (ADX): {trend['trend_strength']:.2f}")
        
        # Генерация сигнала
        signal = generate_signal(symbol, df)
        
        if signal:
            # Создание директории для графиков, если её нет
            os.makedirs('charts', exist_ok=True)
            
            # Создание графика с отметкой сигнала
            chart_filename = plot_signal(df, symbol, TIMEFRAME, signal['signal'], 
                                       signal['price'], signal['stop_loss'], signal['take_profit'])
            
            logger.info(f"График сохранен в: {chart_filename}")
            
            # Форматирование сообщения
            msg = f"\n{'🟢' if signal['signal'] == 'ПОКУПКА' else '🔴'} {signal['signal']} {symbol}\n"
            msg += f"Сила сигнала: {signal['strength']}\n"
            msg += f"Цена входа: {signal['price']:.2f}$\n"
            msg += f"Стоп-лосс: {signal['stop_loss']:.2f}$ ({STOP_LOSS_PCT*100}%)\n"
            msg += f"Тейк-профит: {signal['take_profit']:.2f}$ ({TAKE_PROFIT_PCT*100}%)\n"
            msg += f"Размер позиции: {signal['position_size']*100:.1f}%\n"
            msg += f"Плечо: {signal['leverage']}x\n"
            
            # Добавление деталей анализа
            analysis = signal['analysis']
            msg += f"\nАнализ тренда:\n"
            msg += f"- Сила тренда: {analysis['trend']['trend_strength']:.2f}\n"
            msg += f"- Тренд EMA: {analysis['trend']['ema_trend']}\n"
            msg += f"- Тренд MACD: {analysis['trend']['macd_trend']}\n"
            msg += f"- Тренд Ишимоку: {analysis['trend']['ichimoku_trend']}\n"
            
            msg += f"\nАнализ импульса:\n"
            msg += f"- RSI: {analysis['momentum']['rsi']:.2f} ({analysis['momentum']['rsi_signal']})\n"
            msg += f"- Стохастик: {analysis['momentum']['stoch_k']:.2f}/{analysis['momentum']['stoch_d']:.2f}\n"
            msg += f"- Williams %R: {analysis['momentum']['williams_r']:.2f} ({analysis['momentum']['williams_signal']})\n"
            msg += f"- Скорость изменения: {analysis['momentum']['roc']:.2f}% ({analysis['momentum']['roc_signal']})\n"
            
            msg += f"\nАнализ объема:\n"
            msg += f"- Всплеск объема: {'Да' if analysis['volume']['volume_spike'] else 'Нет'}\n"
            msg += f"- Тренд индекса силы: {'Положительный' if analysis['volume']['force_trend'] else 'Отрицательный'}\n"
            msg += f"- Тренд OBV: {'Положительный' if analysis['volume']['obv_trend'] else 'Отрицательный'}\n"
            
            msg += f"\nАнализ волатильности:\n"
            msg += f"- ATR: {analysis['volatility']['atr']:.2f} ({analysis['volatility']['atr_percent']:.2f}%)\n"
            msg += f"- Ширина полос Боллинджера: {analysis['volatility']['bb_width']:.2f}\n"
            
            # Отправка сообщения и графика в Telegram
            logger.info("Отправка сообщения в Telegram...")
            send_telegram_message(msg, chart_filename)
            logger.info(f"Сгенерирован сигнал для {symbol}: {signal['signal']}")
        else:
            logger.info("Сигнал не сгенерирован. Проверьте условия в generate_signal.")

    except Exception as e:
        logger.error(f"Ошибка при анализе {symbol}: {str(e)}")
        raise

def main():
    # Выбор тестовой пары (BTC/USDT)
    symbol = SYMBOLS[0]
    
    logger.info(f"Создание тестовых данных для {symbol}...")
    df = create_test_data()
    
    logger.info("Анализ символа и генерация сигнала...")
    test_analyze_symbol(symbol, df)
    
    logger.info("Тест завершен. Проверьте Telegram на наличие сообщения с графиком.")

if __name__ == "__main__":
    main() 