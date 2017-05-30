#!/bin/bash

if [ ! -d networkapi_venv ]; then
    virtualenv networkapi_venv
fi

source networkapi_venv/bin/activate

pip install -r requirements.txt

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings'

echo "exporting NETWORKAPI_DEBUG=1"
export NETWORKAPI_DEBUG=1

echo "exporting NETWORKAPI_ALLOWED_HOSTS=10.0.0.2,localhost,127.0.0.1"
export NETWORKAPI_ALLOWED_HOSTS=10.0.0.2,localhost,127.0.0.1

echo "exporting NETWORKAPI_BROKER_DESTINATION"
export NETWORKAPI_BROKER_DESTINATION='networkapi'

echo "exporting NETWORKAPI_BROKER_URI"
export NETWORKAPI_BROKER_URI='tcp://localhost:61613'

echo "Starting ActiveMQ message broker"
sudo service activemq start

echo "Starting RabbitMQ message broker"
sudo service rabbitmq start

echo "clearing memcached:"
echo 'flush_all' | nc localhost 11211

echo "killing gunicorn"
sudo killall gunicorn

echo "cleaning up .pyc"
python /vagrant/manage.py clean_pyc --path /vagrant/networkapi/

echo "starting gunicorn"
/usr/local/bin/gunicorn -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
