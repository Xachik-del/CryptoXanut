# indicators.py

from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator, IchimokuIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator, ForceIndexIndicator
import numpy as np

def add_indicators(df):
    # Short-term Trend Indicators
    macd = MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_histogram"] = macd.macd_diff()
    
    # Fast Moving Averages for short-term trading
    df["ema8"] = EMAIndicator(close=df["close"], window=8).ema_indicator()
    df["ema13"] = EMAIndicator(close=df["close"], window=13).ema_indicator()
    df["ema21"] = EMAIndicator(close=df["close"], window=21).ema_indicator()
    
    # Momentum Indicators
    df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
    
    # Fast Stochastic for short-term
    stoch = StochasticOscillator(high=df["high"], low=df["low"], close=df["close"], window=14, smooth_window=3)
    df["stoch_k"] = stoch.stoch()
    df["stoch_d"] = stoch.stoch_signal()
    
    # Williams %R for short-term reversals
    df["williams_r"] = WilliamsRIndicator(high=df["high"], low=df["low"], close=df["close"]).williams_r()
    
    # Volatility Indicators
    bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
    
    # ATR for volatility and stop loss calculation
    df["atr"] = AverageTrueRange(high=df["high"], low=df["low"], close=df["close"]).average_true_range()
    
    # Volume Indicators
    df["vwap"] = VolumeWeightedAveragePrice(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        volume=df["volume"]
    ).volume_weighted_average_price()
    
    df["obv"] = OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"]).on_balance_volume()
    
    # Force Index for volume-price relationship
    df["force_index"] = ForceIndexIndicator(close=df["close"], volume=df["volume"]).force_index()
    
    # Trend Strength
    adx = ADXIndicator(high=df["high"], low=df["low"], close=df["close"])
    df["adx"] = adx.adx()
    df["adx_pos"] = adx.adx_pos()
    df["adx_neg"] = adx.adx_neg()
    
    # Ichimoku Cloud for trend direction
    ichimoku = IchimokuIndicator(high=df["high"], low=df["low"])
    df["ichimoku_a"] = ichimoku.ichimoku_a()
    df["ichimoku_b"] = ichimoku.ichimoku_b()
    df["ichimoku_base"] = ichimoku.ichimoku_base_line()
    df["ichimoku_conv"] = ichimoku.ichimoku_conversion_line()
    
    # Price action patterns
    df["body_size"] = abs(df["close"] - df["open"])
    df["upper_shadow"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["lower_shadow"] = df[["open", "close"]].min(axis=1) - df["low"]
    
    # Volume analysis
    df["volume_ma"] = df["volume"].rolling(window=20).mean()
    df["volume_std"] = df["volume"].rolling(window=20).std()
    df["volume_ratio"] = df["volume"] / df["volume_ma"]
    
    # Momentum oscillators
    df["momentum"] = df["close"] - df["close"].shift(4)
    df["rate_of_change"] = df["close"].pct_change(periods=4) * 100
    
    return df
