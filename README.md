### Настройка окружения
В файле .env прописать переменные


### Запуск бэкенда
```
cd backend
pip install -r requirements.txt
python manage.py migrate
uvicorn config.asgi:application --reload
```
### Запуск бота
```
cd tg_bots/predict_bot
pip install -r requirements.txt
python bot.py
```