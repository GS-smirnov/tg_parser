#!/bin/bash

python manage.py migrate

sleep 2

uvicorn config.asgi:application --host 0.0.0.0 --port 8000