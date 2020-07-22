#!/bin/bash

DIR="/home/crm/"
WORKERS=3
IP="0.0.0.0:8000"

echo "Запуск crm"

cd $DIR

source venv/bin/activate
python manage.py collectstatic --noinput

exec uvicorn crm.asgi:application --reload --host 0.0.0.0 --port 8000