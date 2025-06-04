# notifier.py

import requests
import logging
import time
from bot.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_telegram_credentials():
    """Проверка валидности токена и chat_id"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                logger.info(f"Подключение к боту {bot_info['result']['username']} установлено.")
                return True
            else:
                logger.error("Ошибка при проверке токена Telegram.")
                return False
        else:
            logger.error(f"Ошибка при проверке токена Telegram: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при проверке токена Telegram: {str(e)}")
        return False

def send_telegram_message(message, image_path=None):
    """
    Отправка сообщения в Telegram
    
    Args:
        message (str): Текст сообщения
        image_path (str, optional): Путь к изображению для отправки
    """
    if not verify_telegram_credentials():
        logger.error("Не удалось отправить сообщение: неверные учетные данные Telegram.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info("Сообщение успешно отправлено в Telegram.")
                
                # Если есть изображение, отправляем его
                if image_path:
                    send_telegram_image(image_path)
                return
            else:
                logger.error(f"Ошибка при отправке сообщения: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))

def send_telegram_image(image_path):
    """
    Отправка изображения в Telegram
    
    Args:
        image_path (str): Путь к изображению
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data = {
        "chat_id": TELEGRAM_CHAT_ID
    }
    files = {
        "photo": open(image_path, "rb")
    }
    
    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            logger.info("Изображение успешно отправлено в Telegram.")
        else:
            logger.error(f"Ошибка при отправке изображения: {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {str(e)}")
    finally:
        files["photo"].close()

def test_telegram_connection():
    """Отправка тестового сообщения для проверки подключения"""
    if verify_telegram_credentials():
        send_telegram_message("Тестовое сообщение: бот работает!")
        logger.info("Тестовое сообщение отправлено.")

if __name__ == "__main__":
    test_telegram_connection()
