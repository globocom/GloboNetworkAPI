#!/bin/bash

export NETWORKAPI_DATABASE_NAME=networkapi_qa01
# export NETWORKAPI_DATABASE_USER=root
# export NETWORKAPI_DATABASE_PASSWORD=
# export NETWORKAPI_DATABASE_HOST=localhost
# export NETWORKAPI_DATABASE_PORT=3306

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings'

echo "exporting NETWORKAPI_DEBUG=1"
export NETWORKAPI_DEBUG=1

echo "exporting NETWORKAPI_BROKER_DESTINATION"
export NETWORKAPI_BROKER_DESTINATION='networkapi'

echo "exporting NETWORKAPI_BROKER_URI"
export NETWORKAPI_BROKER_URI='tcp://localhost:61613'

echo "clearing memcached:"
echo 'flush_all' | nc localhost 11211

echo "killing gunicorn"
sudo killall gunicorn

echo "cleaning up .pyc"
python /vagrant/manage.py clean_pyc --path /vagrant/networkapi/

echo "starting gunicorn"
/usr/local/bin/gunicorn -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
