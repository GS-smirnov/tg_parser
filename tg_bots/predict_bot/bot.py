import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import os
from parser import scroll_and_extract_posts  # Импортируем функцию парсинга
import asyncio

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
PREDICT_API_URL = os.getenv('PREDICT_API_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Получить предсказание', callback_data='get_prediction'))
    keyboard.add(InlineKeyboardButton('Парсить новости', callback_data='parse_news'))
    await message.reply("Добро пожаловать! Нажмите кнопку ниже, чтобы получить предсказание или парсить новости.", reply_markup=keyboard)

@dp.callback_query_handler(Text(equals='get_prediction'))
async def process_get_prediction(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите название компании:")

@dp.callback_query_handler(Text(equals='parse_news'))
async def process_parse_news(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите название канала в формате @channel:")

@dp.message_handler()
async def handle_messages(message: types.Message):
    if message.text.startswith('@'):
        await process_channel_name(message)
    else:
        await process_company_name(message)

async def process_company_name(message: types.Message):
    company_name = message.text
    try:
        response = requests.get(PREDICT_API_URL, params={'channel': company_name})
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

async def process_channel_name(message: types.Message):
    channel_name = message.text
    url = f"https://t.me/s/{channel_name.lstrip('@')}"
    await message.reply(f"Парсинг новостей из канала: {channel_name}...")

    loop = asyncio.get_event_loop()
    posts = await loop.run_in_executor(None, scroll_and_extract_posts, url, 2, 10)

    if posts:
        # Отправка постов на бэкенд
        for post in posts:
            data = {
                'channel': channel_name,
                'text': post
            }
            response = requests.post(PREDICT_API_URL, json=data)
            if response.status_code == 201:
                await message.reply(f"Сообщение сохранено: {post[:30]}...")
            else:
                await message.reply(f"Ошибка при сохранении сообщения: {response.status_code}")
    else:
        await message.reply("Не удалось получить посты из канала. Пожалуйста, попробуйте снова.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
