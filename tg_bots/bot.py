import logging
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
TELETHON_API_ID = os.getenv('TELETHON_API_ID')
TELETHON_API_HASH = os.getenv('TELETHON_API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
API_URL = os.getenv('API_URL')
CHANNEL_MESSAGES_URL = os.getenv('CHANNEL_MESSAGES_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения данных пользователей
user_data = {}

# Загрузка строки сессии из файла
session_file = 'session.txt'
if os.path.exists(session_file):
    with open(session_file, 'r') as file:
        session_string = file.read().strip()
else:
    session_string = None

if not session_string:
    raise ValueError("Session file not found or empty. Please provide a valid session file.")

# Настройки клиента Telethon
telethon_client = TelegramClient(StringSession(session_string), TELETHON_API_ID, TELETHON_API_HASH)

def contains_keywords(message, keywords):
    for keyword in keywords:
        if re.search(keyword, message, re.IGNORECASE):
            return True
    return False

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне канал в формате @channel и ключевые слова через запятую.")

@dp.message_handler(commands=['get'])
async def get_channel_messages(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Пожалуйста, укажите канал в формате @channel.")
        return
    
    channel = parts[1]
    try:
        response = requests.get(CHANNEL_MESSAGES_URL, params={'channel': channel})
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                for msg in data:
                    await message.reply(f"Сообщение из {channel}:\n{msg['text']}")
            else:
                await message.reply(f"Нет сообщений для канала {channel}.")
        else:
            await message.reply(f"Ошибка при получении сообщений: {response.status_code}")
    except Exception as e:
        logging.exception(e)
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler()
async def process_message(message: types.Message):
    try:
        if message.text.startswith('@'):
            parts = message.text.split()
            if len(parts) < 2:
                await message.reply("Пожалуйста, укажите канал и ключевые слова через запятую.")
                return
            
            channel = parts[0]
            keywords = parts[1].split(',')

            user_data[message.from_user.id] = {'channel': channel, 'keywords': keywords}
            await message.reply(f"Канал: {channel}\nКлючевые слова: {', '.join(keywords)}")

            await parse_and_send_messages(message.from_user.id)
        else:
            await message.reply("Пожалуйста, укажите канал в формате @channel и ключевые слова через запятую.")
    except Exception as e:
        logging.exception(e)
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте снова.")

async def parse_and_send_messages(user_id):
    if user_id not in user_data:
        return

    data = user_data[user_id]
    channel = data['channel']
    keywords = data['keywords']

    # Обертка для старта клиента Telethon и сохранения сессии
    async with telethon_client:
        if not telethon_client.is_connected():
            await telethon_client.connect()

        if not await telethon_client.is_user_authorized():
            print("Unauthorized session, please log in using a valid session file.")
            return

        async for message in telethon_client.iter_messages(channel):
            message_text = message.text
            if message_text and contains_keywords(message_text, keywords):
                data = {
                    'channel': channel,
                    'message_id': message.id,
                    'text': message_text,
                    'date': message.date.isoformat()
                }
                response = requests.post(API_URL, json=data)
                if response.status_code == 201:
                    await bot.send_message(user_id, f'Сообщение сохранено: {message_text}')
                else:
                    await bot.send_message(user_id, f'Ошибка при сохранении сообщения: {response.status_code}')

        @telethon_client.on(events.NewMessage(chats=PeerChannel(channel)))
        async def handler(event):
            message_text = event.message.message
            if message_text and contains_keywords(message_text, keywords):
                data = {
                    'channel': event.chat_id,
                    'message_id': event.message.id,
                    'text': message_text,
                    'date': event.message.date.isoformat()
                }
                response = requests.post(API_URL, json=data)
                if response.status_code == 201:
                    await bot.send_message(user_id, f'Новое сообщение сохранено: {message_text}')
                else:
                    await bot.send_message(user_id, f'Ошибка при сохранении сообщения: {response.status_code}')

        await telethon_client.run_until_disconnected()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
