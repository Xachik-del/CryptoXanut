# notifier.py

import requests
import logging
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

logger = logging.getLogger(__name__)

def verify_telegram_credentials():
    """Verify that the Telegram token and chat ID are valid"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                logger.info(f"Successfully connected to Telegram bot: {bot_info['result']['username']}")
                return True
            else:
                logger.error("Invalid Telegram token")
                return False
        else:
            logger.error(f"Failed to verify Telegram token. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error verifying Telegram credentials: {str(e)}")
        return False

def send_telegram_message(message, max_retries=3):
    """
    Send a message to Telegram with retry mechanism and proper error handling
    
    Args:
        message (str): Message to send
        max_retries (int): Maximum number of retry attempts
    """
    if not verify_telegram_credentials():
        logger.error("Cannot send message: Invalid Telegram credentials")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Format message with timestamp and proper formatting
    formatted_message = (
        f"🤖 *Crypto Futures Signal*\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"{message}"
    )
    
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": formatted_message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            if response.json().get("ok"):
                logger.info("Message successfully sent to Telegram")
                return True
            else:
                error_msg = response.json().get("description", "Unknown error")
                logger.error(f"Failed to send message: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue
            
        except Exception as e:
            logger.error(f"Unexpected error while sending message: {str(e)}")
            return False
    
    logger.error(f"Failed to send message after {max_retries} attempts")
    return False

def test_telegram_connection():
    """Test the Telegram connection and send a test message"""
    if verify_telegram_credentials():
        test_message = (
            "🔔 *Test Message*\n\n"
            "This is a test message to verify that the Telegram bot is working correctly.\n"
            "If you receive this message, the notification system is properly configured."
        )
        return send_telegram_message(test_message)
    return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the Telegram connection
    test_telegram_connection()
