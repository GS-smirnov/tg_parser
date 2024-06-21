FROM python:3.10-slim

WORKDIR /bot

COPY requirements.txt /bot/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /bot/

CMD ["python", "bot.py"]