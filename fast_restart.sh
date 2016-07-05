#!/bin/bash
sudo killall gunicorn
python manage.py clean_pyc --path /vagrant/networkapi/
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
tail -f /tmp/networkapi.log
