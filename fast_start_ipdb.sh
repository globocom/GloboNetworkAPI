#!/bin/bash
# virtualenv ipdb_env
source ipdb_env/bin/activate
# pip install -r requirements.txt
# pip install -r requirements_debug.txt
echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_DEBUG=1

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ipdb'

echo "exporting NETWORKAPI_BROKER_DESTINATION"
export NETWORKAPI_BROKER_DESTINATION='networkapi'

echo "exporting NETWORKAPI_BROKER_URI"
export NETWORKAPI_BROKER_URI='tcp://localhost:61613'

echo "clearing memcached:"
echo 'flush_all' | nc localhost 11211

echo "cleaning up .pyc"
python manage.py clean_pyc --path /vagrant/networkapi/

killall rqworker.sh
./rqworker.sh &

echo "starting runserver 0.0.0.0:8001 --ipdb"
python manage.py runserver 0.0.0.0:8001 --ipdb
