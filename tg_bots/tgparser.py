from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scroll_and_extract_posts(driver, url, scroll_pause_time=2, max_scrolls=10):
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")
    posts = []

    for _ in range(max_scrolls):
        # Прокручиваем страницу вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Ждем загрузки новых данных
        time.sleep(scroll_pause_time)

        # Извлекаем содержимое страницы
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Извлекаем блоки с постами
        post_blocks = soup.find_all('div', class_='tgme_widget_message_wrap')
        
        for block in post_blocks:
            text_div = block.find('div', class_='tgme_widget_message_text')
            if text_div:
                posts.append(text_div.get_text(strip=True))

        # Проверяем высоту страницы после прокрутки
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return posts

# Настройка Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    url = 'https://t.me/s/whackdoor'
    posts = scroll_and_extract_posts(driver, url, max_scrolls=20)  # Увеличьте max_scrolls для большего количества прокруток
    for i, post in enumerate(posts, start=1):
        print(f"Post {i}:\n{post}\n")

    # Сохраняем посты в текстовый файл
    with open('telegram_posts.txt', 'w', encoding='utf-8') as f:
        for post in posts:
            f.write(post + '\n\n')
finally:
    driver.quit()
