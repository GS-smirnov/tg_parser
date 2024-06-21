import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

api_id = os.getenv('TELETHON_API_ID')
api_hash = os.getenv('TELETHON_API_HASH')

# Загрузка строки сессии из файла
with open('session.txt', 'r') as file:
    session_string = file.read().strip()

# Создание клиента с сохраненной сессией
client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    await client.start()

    # Теперь вы можете выполнять любые действия, как обычно
    me = await client.get_me()
    print(me.stringify())

with client:
    client.loop.run_until_complete(main())
