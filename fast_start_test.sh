#!/bin/sh

pip install -r requirements_test.txt

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_LOG_QUEUE=0

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

# Updates the SDN controller ip address
export REMOTE_CTRL_IP=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
echo "Found SDN controller at $REMOTE_CTRL_IP"

echo "Starting tests.."
python manage.py test "$@"
