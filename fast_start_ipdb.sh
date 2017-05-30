#!/bin/bash
if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

source test_venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt

echo "exporting NETWORKAPI_DEBUG=0"
export NETWORKAPI_DEBUG=0

echo "NETWORKAPI_LOG_FILE=/tmp/networkapi.log"
export NETWORKAPI_LOG_FILE='/tmp/networkapi.log'

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ipdb'

echo "exporting NETWORKAPI_ALLOWED_HOSTS=10.0.0.2,localhost,127.0.0.1"
export NETWORKAPI_ALLOWED_HOSTS=10.0.0.2,localhost,127.0.0.1

echo "cleaning up .pyc"
python manage.py clean_pyc --path /vagrant/networkapi/

echo "starting runserver 0.0.0.0:8001 --ipdb"
python manage.py runserver 0.0.0.0:8001 --ipdb
