from bs4 import BeautifulSoup
import requests
from .models import Messages
import datetime


def parse_telegram_channel(channel_name):
    try:
        url = f'https://t.me/s/{channel_name}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            post_blocks = soup.find_all('div', class_='tgme_widget_message_wrap')

            for block in post_blocks:
                text_div = block.find('div', class_='tgme_widget_message_text')
                if text_div:
                    post_text = text_div.get_text(strip=True)
                    post_date = block.find('time')['datetime']
                    post_date = datetime.datetime.fromisoformat(post_date)

                    Messages.objects.update_or_create(
                        channel=channel_name,
                        text=post_text,
                        defaults={'date': post_date}
                    )
        else:
            print(f"Failed to retrieve data for {channel_name}")

    except Exception as e:
        print(e)
