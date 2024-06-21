import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
PREDICT_API_URL = os.getenv('PREDICT_API_URL')
PARSE_API_URL = os.getenv('PARSE_API_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Получить предсказание', callback_data='get_prediction'))
    keyboard.add(InlineKeyboardButton('Запустить парсинг', callback_data='start_parsing'))
    await message.reply("Добро пожаловать! Нажмите кнопку ниже, чтобы получить предсказание или запустить парсинг.", reply_markup=keyboard)

@dp.callback_query_handler(Text(equals='get_prediction'))
async def process_get_prediction(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите название компании:")

@dp.callback_query_handler(Text(equals='start_parsing'))
async def process_start_parsing(callback_query: types.CallbackQuery):
    try:
        response = requests.post(PARSE_API_URL)
        if response.status_code == 200:
            await bot.send_message(callback_query.from_user.id, "Парсинг успешно запущен.")
        else:
            await bot.send_message(callback_query.from_user.id, f"Ошибка при запуске парсинга: {response.status_code}")
    except Exception as e:
        logging.exception(e)
        await bot.send_message(callback_query.from_user.id, "Произошла ошибка при запуске парсинга. Пожалуйста, попробуйте снова.")

@dp.message_handler()
async def process_company_name(message: types.Message):
    company_name = message.text
    try:
        response = requests.get(PREDICT_API_URL, params={'company': company_name})
        if response.status_code == 200:
            data = response.json().get('data', {})
            prediction = data.get('prediction', 'Нет доступных предсказаний')
            await message.reply(f"Предсказание для {company_name}:\n{prediction}")
        elif response.status_code == 404:
            await message.reply(f"Предсказание для {company_name} не найдено.")
        else:
            await message.reply(f"Ошибка при получении предсказания: {response.status_code}")
    except Exception as e:
        logging.exception(e)
        await message.reply("Произошла ошибка при получении предсказания. Пожалуйста, попробуйте снова.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
