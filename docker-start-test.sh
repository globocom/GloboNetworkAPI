#!/bin/bash

if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

source test_venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt

export NETWORKAPI_DEBUG=DEBUG
export CI=1
export NETWORKAPI_DATABASE_OPTIONS='{"init_command": "SET default_storage_engine=INNODB"}'
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'
export REMOTE_CTRL_IP=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')

echo "Starting tests.."
python manage.py test "$@"
