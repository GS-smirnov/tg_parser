### Настройка окружения
В файле .env прописать переменные

### Установка библиотек
```
pip install -r requirements.txt
```

### Запуск бэкенда
```
cd telegram_backend
python manage.py migrate
uvicorn config.asgi:application --reload
```
### Запуск бота
```
python bot.py
```