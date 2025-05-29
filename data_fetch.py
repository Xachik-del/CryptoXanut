# data_fetch.py

import ccxt
import pandas as pd
import logging
from datetime import datetime, timedelta
import time
import numpy as np

logger = logging.getLogger(__name__)

def fetch_ohlcv(symbol, exchange, timeframe, limit=500):
    """
    Fetch OHLCV data from exchange with retry mechanism and proper error handling
    
    Args:
        symbol (str): Trading pair symbol
        exchange (ccxt.Exchange): Exchange instance
        timeframe (str): Timeframe for the data
        limit (int): Number of candles to fetch
        
    Returns:
        pd.DataFrame: DataFrame with OHLCV data
    """
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Fetch OHLCV data
            ohlcv = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            
            # Add additional time-based features
            df["hour"] = df["timestamp"].dt.hour
            df["day_of_week"] = df["timestamp"].dt.dayofweek
            
            # Calculate returns
            df["returns"] = df["close"].pct_change()
            df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
            
            # Calculate volatility
            df["volatility"] = df["returns"].rolling(window=20).std()
            
            # Calculate price ranges
            df["price_range"] = df["high"] - df["low"]
            df["body_size"] = abs(df["close"] - df["open"])
            
            # Calculate volume metrics
            df["volume_ma"] = df["volume"].rolling(window=20).mean()
            df["volume_std"] = df["volume"].rolling(window=20).std()
            
            # Clean up data
            df = df.dropna()
            
            logger.info(f"Successfully fetched {len(df)} candles for {symbol}")
            return df
            
        except ccxt.NetworkError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Network error while fetching {symbol}, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts: {str(e)}")
                raise
                
        except ccxt.ExchangeError as e:
            logger.error(f"Exchange error while fetching {symbol}: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error while fetching {symbol}: {str(e)}")
            raise

def validate_data(df, symbol):
    """
    Validate the fetched data for quality and completeness
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        symbol (str): Symbol for logging purposes
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    if df.empty:
        logger.error(f"Empty dataset received for {symbol}")
        return False
        
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        logger.warning(f"Missing values found in {symbol} data:\n{missing_values}")
        return False
        
    # Check for zero or negative prices
    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        logger.error(f"Invalid price values found in {symbol} data")
        return False
        
    # Check for zero or negative volume
    if (df["volume"] < 0).any():
        logger.error(f"Invalid volume values found in {symbol} data")
        return False
        
    # Check for price consistency
    if not ((df["high"] >= df["low"]) & (df["high"] >= df["open"]) & 
            (df["high"] >= df["close"]) & (df["low"] <= df["open"]) & 
            (df["low"] <= df["close"])).all():
        logger.error(f"Price consistency check failed for {symbol}")
        return False
        
    return True
