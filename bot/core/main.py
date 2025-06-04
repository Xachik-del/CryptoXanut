# main.py

import ccxt
import time
import logging
import signal
import sys
from datetime import datetime
from bot.config import (
    SYMBOLS, FUTURES_INTERVAL, TIMEFRAME, LEVERAGE,
    BINANCE_API_KEY, BINANCE_API_SECRET
)
from bot.core.strategy import analyze_symbol
from bot.data.data_fetch import fetch_ohlcv, validate_data
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'futures_analysis_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info("Received shutdown signal. Gracefully stopping...")
    running = False

def initialize_exchange():
    """Initialize and configure the exchange connection for futures trading"""
    try:
        if not BINANCE_API_KEY or not BINANCE_API_SECRET:
            logger.error("Binance API credentials are not configured. Please add your API key and secret in config.py")
            sys.exit(1)

        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use futures market
                'adjustForTimeDifference': True,
                'defaultContractType': 'perpetual',  # Use perpetual futures
                'createMarketBuyOrderRequiresPrice': False
            }
        })
        
        # Test connection and verify permissions
        try:
            # First, test basic API access
            exchange.load_markets()
            logger.info("Successfully connected to Binance Futures")
            
            # Test futures permissions by getting account info
            account_info = exchange.fetch_balance()
            logger.info("Successfully verified futures trading permissions")
            
            # Set leverage for all symbols
            for symbol in SYMBOLS:
                try:
                    exchange.set_leverage(LEVERAGE, symbol)
                    logger.info(f"Set leverage to {LEVERAGE}x for {symbol}")
                except ccxt.AuthenticationError as e:
                    logger.error(f"Authentication error for {symbol}: {str(e)}")
                    logger.error("Please check your API key permissions in Binance:")
                    logger.error("1. Go to API Management")
                    logger.error("2. Enable 'Enable Futures' permission")
                    logger.error("3. Enable 'Enable Reading' permission")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Failed to set leverage for {symbol}: {str(e)}")
                    continue
            
            return exchange
            
        except ccxt.AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            logger.error("Please check your API key permissions in Binance:")
            logger.error("1. Go to API Management")
            logger.error("2. Enable 'Enable Futures' permission")
            logger.error("3. Enable 'Enable Reading' permission")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Failed to initialize exchange: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception args: {e.args}")
        logger.error("Traceback:\n" + traceback.format_exc())
        raise

def run_bot():
    """Main bot loop with proper error handling and logging"""
    logger.info("Starting futures trading bot...")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        exchange = initialize_exchange()
        
        while running:
            cycle_start = time.time()
            logger.info("Starting new analysis cycle...")
            
            for symbol in SYMBOLS:
                try:
                    logger.info(f"Analyzing {symbol}...")
                    
                    # Fetch and validate data
                    df = fetch_ohlcv(symbol, exchange, timeframe=TIMEFRAME)
                    if not validate_data(df, symbol):
                        logger.error(f"Skipping {symbol} due to invalid data")
                        continue
                    
                    # Analyze symbol
                    analyze_symbol(symbol, exchange)
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {str(e)}")
                    continue
            
            # Calculate sleep time to maintain consistent intervals
            elapsed = time.time() - cycle_start
            sleep_time = max(0, FUTURES_INTERVAL - elapsed)
            
            if running:  # Only sleep if we're still running
                logger.info(f"Cycle completed in {elapsed:.2f} seconds. Sleeping for {sleep_time:.2f} seconds...")
                # Split sleep into smaller intervals to allow for graceful shutdown
                while sleep_time > 0 and running:
                    sleep_interval = min(sleep_time, 1.0)  # Sleep in 1-second intervals
                    time.sleep(sleep_interval)
                    sleep_time -= sleep_interval
    
    except Exception as e:
        logger.error(f"Fatal error in main loop: {str(e)}")
        raise
    
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {str(e)}")
        sys.exit(1)
