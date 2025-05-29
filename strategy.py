# strategy.py

from indicators import add_indicators
from notifier import send_telegram_message
from data_fetch import fetch_ohlcv
from config import (
    TIMEFRAME, RSI_OVERSOLD, RSI_OVERBOUGHT, STOCH_OVERSOLD,
    STOCH_OVERBOUGHT, ADX_THRESHOLD, VOLUME_THRESHOLD,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT, LEVERAGE
)
import logging
import pandas as pd
import numpy as np

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_trend(df):
    """Анализ краткосрочного тренда с использованием нескольких индикаторов"""
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # Сила тренда с использованием ADX
    trend_strength = last_row["adx"]
    is_strong_trend = trend_strength > ADX_THRESHOLD
    
    # Тренд быстрых EMA
    ema_trend = "бычий" if last_row["ema8"] > last_row["ema13"] > last_row["ema21"] else "медвежий"
    
    # Тренд MACD с гистограммой
    macd_trend = "бычий" if (last_row["macd"] > last_row["macd_signal"] and 
                              last_row["macd_histogram"] > prev_row["macd_histogram"]) else "медвежий"
    
    # Тренд Ишимоку
    ichimoku_trend = "бычий" if (last_row["close"] > last_row["ichimoku_a"] and 
                                  last_row["ichimoku_a"] > last_row["ichimoku_b"]) else "медвежий"
    
    return {
        "trend_strength": trend_strength,
        "is_strong_trend": is_strong_trend,
        "ema_trend": ema_trend,
        "macd_trend": macd_trend,
        "ichimoku_trend": ichimoku_trend
    }

def analyze_momentum(df):
    """Анализ краткосрочного импульса"""
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # Анализ RSI с дивергенцией
    rsi = last_row["rsi"]
    rsi_signal = "перепродан" if rsi < RSI_OVERSOLD else "перекуплен" if rsi > RSI_OVERBOUGHT else "нейтральный"
    
    # Анализ Стохастика
    stoch_k = last_row["stoch_k"]
    stoch_d = last_row["stoch_d"]
    stoch_signal = "перепродан" if stoch_k < STOCH_OVERSOLD and stoch_d < STOCH_OVERSOLD else \
                  "перекуплен" if stoch_k > STOCH_OVERBOUGHT and stoch_d > STOCH_OVERBOUGHT else "нейтральный"
    
    # Williams %R
    williams_r = last_row["williams_r"]
    williams_signal = "перепродан" if williams_r < -80 else "перекуплен" if williams_r > -20 else "нейтральный"
    
    # Скорость изменения
    roc = last_row["rate_of_change"]
    roc_signal = "бычий" if roc > 0 and roc > prev_row["rate_of_change"] else "медвежий"
    
    return {
        "rsi": rsi,
        "rsi_signal": rsi_signal,
        "stoch_k": stoch_k,
        "stoch_d": stoch_d,
        "stoch_signal": stoch_signal,
        "williams_r": williams_r,
        "williams_signal": williams_signal,
        "roc": roc,
        "roc_signal": roc_signal
    }

def analyze_volatility(df):
    """Анализ волатильности и паттернов цены"""
    last_row = df.iloc[-1]
    
    # Анализ полос Боллинджера
    bb_width = last_row["bb_width"]
    price_position = (last_row["close"] - last_row["bb_lower"]) / (last_row["bb_upper"] - last_row["bb_lower"])
    
    # Анализ ATR
    atr = last_row["atr"]
    atr_percent = (atr / last_row["close"]) * 100
    
    # Паттерны цены
    body_size = last_row["body_size"]
    upper_shadow = last_row["upper_shadow"]
    lower_shadow = last_row["lower_shadow"]
    
    return {
        "bb_width": bb_width,
        "price_position": price_position,
        "atr": atr,
        "atr_percent": atr_percent,
        "body_size": body_size,
        "upper_shadow": upper_shadow,
        "lower_shadow": lower_shadow,
        "is_volatile": bb_width > df["bb_width"].mean() * VOLUME_THRESHOLD
    }

def analyze_volume(df):
    """Анализ паттернов объема и силы"""
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # Тренд объема
    volume_trend = df["volume"].iloc[-5:].mean() > df["volume"].iloc[-10:-5].mean()
    
    # Всплеск объема
    volume_spike = last_row["volume"] > (df["volume_ma"].iloc[-1] + 2 * df["volume_std"].iloc[-1])
    
    # Индекс силы
    force_index = last_row["force_index"]
    force_trend = force_index > prev_row["force_index"]
    
    # Тренд OBV
    obv_trend = last_row["obv"] > prev_row["obv"]
    
    return {
        "volume_trend": volume_trend,
        "volume_spike": volume_spike,
        "force_index": force_index,
        "force_trend": force_trend,
        "obv_trend": obv_trend,
        "vwap": last_row["vwap"]
    }

def calculate_position_size(price, atr):
    """Расчет размера позиции на основе ATR и управления рисками"""
    risk_per_trade = 0.01  # 1% риска на сделку
    stop_loss_atr = 2  # Стоп-лосс в единицах ATR
    
    stop_loss = atr * stop_loss_atr
    position_size = risk_per_trade / (stop_loss / price)
    
    return min(position_size, 1.0)  # Ограничение в 100% доступной маржи

def generate_signal(symbol, df):
    """Генерация торгового сигнала на основе комплексного анализа"""
    trend = analyze_trend(df)
    momentum = analyze_momentum(df)
    volatility = analyze_volatility(df)
    volume = analyze_volume(df)
    
    last_row = df.iloc[-1]
    close_price = last_row["close"]
    
    # Расчет размера позиции и уровней стопов
    position_size = calculate_position_size(close_price, last_row["atr"])
    stop_loss = close_price * (1 - STOP_LOSS_PCT)
    take_profit = close_price * (1 + TAKE_PROFIT_PCT)
    
    # Логирование текущих условий
    logger.info(f"\nАнализ условий для {symbol}:")
    logger.info(f"Сила тренда: {trend['trend_strength']:.2f} (Порог: {ADX_THRESHOLD})")
    logger.info(f"RSI: {momentum['rsi']:.2f} (Перепродан: {RSI_OVERSOLD}, Перекуплен: {RSI_OVERBOUGHT})")
    logger.info(f"Стохастик: {momentum['stoch_k']:.2f}/{momentum['stoch_d']:.2f}")
    logger.info(f"Всплеск объема: {volume['volume_spike']}")
    
    # Условия для сильного сигнала на покупку (ослабленные)
    if (trend["is_strong_trend"] and
        (trend["ema_trend"] == "бычий" or trend["macd_trend"] == "бычий") and
        momentum["rsi_signal"] == "перепродан" and
        (momentum["stoch_signal"] == "перепродан" or momentum["williams_signal"] == "перепродан") and
        volume["volume_spike"]):
        
        return {
            "signal": "ПОКУПКА",
            "strength": "СИЛЬНЫЙ",
            "price": close_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "leverage": LEVERAGE,
            "analysis": {
                "trend": trend,
                "momentum": momentum,
                "volatility": volatility,
                "volume": volume
            }
        }
    
    # Условия для сильного сигнала на продажу (ослабленные)
    elif (trend["is_strong_trend"] and
          (trend["ema_trend"] == "медвежий" or trend["macd_trend"] == "медвежий") and
          momentum["rsi_signal"] == "перекуплен" and
          (momentum["stoch_signal"] == "перекуплен" or momentum["williams_signal"] == "перекуплен") and
          volume["volume_spike"]):
        
        return {
            "signal": "ПРОДАЖА",
            "strength": "СИЛЬНЫЙ",
            "price": close_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "leverage": LEVERAGE,
            "analysis": {
                "trend": trend,
                "momentum": momentum,
                "volatility": volatility,
                "volume": volume
            }
        }
    
    return None

def analyze_symbol(symbol, exchange):
    try:
        # Получение и подготовка данных
        df = fetch_ohlcv(symbol, exchange, timeframe=TIMEFRAME)
        df = add_indicators(df)
        
        # Генерация сигнала
        signal = generate_signal(symbol, df)
        
        if signal:
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
            
            send_telegram_message(msg)
            logger.info(f"Сгенерирован сигнал для {symbol}: {signal['signal']}")
        
    except Exception as e:
        logger.error(f"Ошибка при анализе {symbol}: {str(e)}")
        raise
