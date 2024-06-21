FROM python:3.10-slim

WORKDIR /backend

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

COPY start.sh /backend/start.sh

RUN chmod +x start.sh

ENTRYPOINT ["./start.sh"]

