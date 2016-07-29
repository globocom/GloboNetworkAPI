#!/bin/bash
echo "clearing memcached:"
echo 'flush_all' | nc localhost 11211
echo "killing gunicorn"
sudo killall gunicorn
echo "cleaning up .pyc"
python manage.py clean_pyc --path /vagrant/networkapi/
echo "starting gunicorn"
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
tail -f /tmp/networkapi.log
