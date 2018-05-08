#!/bin/bash

if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

source test_venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt

export NETWORKAPI_DEBUG=1
export NETWORKAPI_LOG_QUEUE=0
export DJANGO_SETTINGS_MODULE='networkapi.settings_ipdb'

echo "starting runserver 0.0.0.0:8001 --ipdb"
python manage.py runserver 0.0.0.0:8001
