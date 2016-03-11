#!/bin/bash
find /vagrant/networkapi -name *.pyc -delete
sudo killall gunicorn
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
tail -f /tmp/networkapi.log
