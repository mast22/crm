#!/bin/bash

DIR="/home/kopylov-crm/"
cd $DIR

python3.8 -m venv venv
source venv/bin/activate
exec apk add build-base # для установки uvloop
python -m pip install -r ../requirements.txt
python manage.py migrate
