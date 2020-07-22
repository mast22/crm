#!/bin/bash

DIR="/home/crm/"
cd $DIR

python3.8 -m venv venv
source venv/bin/activate
apk add build-base # для установки uvloop
python manage.py migrate
python -m pip install -r ../requirements.txt
