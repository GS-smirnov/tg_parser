import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import os
import openai

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
PREDICT_API_URL = os.getenv('PREDICT_API_URL')
PARSE_API_URL = os.getenv('PARSE_API_URL')
FILTERED_MESSAGES_URL = os.getenv('FILTERED_MESSAGES_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Получить предсказание', callback_data='get_prediction'))
    keyboard.add(InlineKeyboardButton('Запустить парсинг', callback_data='start_parsing'))
    keyboard.add(InlineKeyboardButton('Фильтровать сообщения', callback_data='filter_messages'))
    await message.reply(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы получить предсказание, запустить парсинг или фильтровать сообщения.",
        reply_markup=keyboard)


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
        await bot.send_message(callback_query.from_user.id,
                               "Произошла ошибка при запуске парсинга. Пожалуйста, попробуйте снова.")


@dp.callback_query_handler(Text(equals='filter_messages'))
async def process_filter_messages(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
                           "Пожалуйста, введите название компании для фильтрации сообщений:")


@dp.message_handler()
async def process_company_name(message: types.Message):
    if 'company' in message.text.lower():
        company_name = message.text.split(' ')[1]
        await filter_messages(message, company_name)
    else:
        company_name = message.text
        await get_prediction(message, company_name)


async def get_prediction(message: types.Message, company_name: str):
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


async def filter_messages(message: types.Message, company_name: str):
    try:
        response = requests.get(FILTERED_MESSAGES_URL, params={'company': company_name})
        if response.status_code == 200:
            messages_data = response.json().get('data', [])
            if not messages_data:
                await message.reply(f"Сообщения для компании {company_name} не найдены.")
                return

            combined_texts = " ".join([msg['text'] for msg in messages_data])
            gpt_response = get_gpt_response(combined_texts)

            await message.reply(f"Результат для {company_name}:\n{gpt_response}")
        else:
            await message.reply(f"Ошибка при получении сообщений: {response.status_code}")
    except Exception as e:
        logging.exception(e)
        await message.reply("Произошла ошибка при получении сообщений. Пожалуйста, попробуйте снова.")


def get_gpt_response(text: str) -> str:
    prompt = f"Analyze the following messages and provide a summary:\n\n{text}"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.exception(e)
        return "Произошла ошибка при обработке текста с помощью GPT-3.5."


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
