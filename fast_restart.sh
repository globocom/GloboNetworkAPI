#!/bin/bash
sudo killall gunicorn
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
tail -f /tmp/networkapi.log
