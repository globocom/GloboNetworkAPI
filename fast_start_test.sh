#!/bin/bash
if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

# if [ -d cover ]; then
#    echo "Removing old cover reports"
#    rm -rf cover/
# fi


source test_venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_DEBUG='INFO'

echo "exporting NETWORKAPI_BROKER_URI"
export NETWORKAPI_BROKER_URI='tcp://localhost:61613'

echo "Starting ActiveMQ message broker"
sudo service activemq start

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'
python manage.py test "$@"
