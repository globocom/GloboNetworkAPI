#!/bin/bash
# export NETWORKAPI_DATABASE_NAME=networkapi
# export NETWORKAPI_DATABASE_USER=root
# export NETWORKAPI_DATABASE_PASSWORD=
# export NETWORKAPI_DATABASE_HOST=localhost
# export NETWORKAPI_DATABASE_PORT=3306
echo "clearing memcached:"
echo 'flush_all' | nc localhost 11211
echo "killing gunicorn"
sudo killall gunicorn
echo "cleaning up .pyc"
python manage.py clean_pyc --path /vagrant/networkapi/
echo "starting gunicorn"
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
tail -f /tmp/networkapi.log
