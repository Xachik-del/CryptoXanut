# Настройка бота на PythonAnywhere

## 1. Регистрация на PythonAnywhere
1. Зарегистрируйтесь на [PythonAnywhere](https://www.pythonanywhere.com/) (бесплатный аккаунт)
2. После регистрации войдите в свой аккаунт

## 2. Загрузка кода
1. В разделе "Files" создайте новую директорию для бота (например, `cryptoxanut`)
2. Загрузите все файлы проекта в эту директорию
   - Можно использовать Git: `git clone https://github.com/your-repo/cryptoxanut.git`
   - Или загрузить файлы через веб-интерфейс

## 3. Настройка виртуального окружения
1. Откройте консоль PythonAnywhere
2. Выполните следующие команды:
```bash
cd cryptoxanut
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Настройка переменных окружения
1. В разделе "Web" создайте новый веб-приложение
2. Выберите "Manual configuration"
3. Выберите Python 3.10
4. В разделе "Code" укажите путь к `wsgi.py`
5. В разделе "Environment variables" добавьте:
```
TELEGRAM_TOKEN=7910233528:AAF9RuaSa_UyxFmgLlAC9REDtG9OfJOHOFE
TELEGRAM_CHAT_ID=705512639
BINANCE_API_KEY=65PXvD8ddnf8efNpy7tc4H5LmBpPIttCOSH8AVGIOyXzfxIHcnUT5duhlnjbVw0d
BINANCE_API_SECRET=rKgV2Cxpg6Ga6XKYpub98SbAyg0rMw1QA61DJPQDG09hiHSJgc9UwqSqnqwXkkCf
```

## 5. Настройка WSGI
1. В разделе "Web" найдите ссылку на WSGI configuration file
2. Замените содержимое файла на код из нашего `wsgi.py`

## 6. Запуск бота
1. В разделе "Web" нажмите кнопку "Reload"
2. Бот должен автоматически запуститься

## Мониторинг
- Логи можно просматривать в разделе "Web" -> "Error log"
- Статус бота можно проверить через Telegram

## Важные замечания
1. Бесплатный аккаунт PythonAnywhere имеет некоторые ограничения:
   - Приложение должно быть доступно по HTTP
   - Ограниченное количество CPU-часов
   - Ограниченное дисковое пространство
2. Бот будет работать, пока веб-приложение активно
3. При необходимости можно настроить автоматический перезапуск через Always-on задачу

## Устранение неполадок
1. Если бот не запускается, проверьте:
   - Логи в разделе "Web" -> "Error log"
   - Правильность путей в WSGI конфигурации
   - Наличие всех переменных окружения
2. Если бот падает, проверьте:
   - Логи на наличие ошибок
   - Достаточность ресурсов (CPU, память)
   - Правильность API ключей 