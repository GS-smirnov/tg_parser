import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

api_id = os.getenv('TELETHON_API_ID')
api_hash = os.getenv('TELETHON_API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

# Создание клиента с временной сессией
client = TelegramClient(StringSession(), api_id, api_hash)

async def main():
    await client.start(phone_number)

    # Сохранение сессии в строковом формате
    session_string = client.session.save()
    print(f'Session string: {session_string}')

    # Используйте эту строку сессии в других скриптах для входа без необходимости повторного ввода кода
    with open('session.txt', 'w') as file:
        file.write(session_string)

with client:
    client.loop.run_until_complete(main())
