from bot.core.main import run_bot
import threading

def application(environ, start_response):
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Возвращаем простой ответ для веб-сервера
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'Bot is running'] 