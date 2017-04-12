#!/bin/bash
if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

source test_venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_DEBUG='DEBUG'

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'
python manage.py test
