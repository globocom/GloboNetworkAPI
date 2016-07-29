#!/bin/bash
echo "exporting NETWORKAPI_PDB"
export NETWORKAPI_PDB=1
echo "clearing memcached:"
echo 'flush_all' | nc localhost 11211
echo "cleaning up .pyc"
python manage.py clean_pyc --path /vagrant/networkapi/
echo "starting runserver 0.0.0.0:8005 --ipdb"
python manage.py runserver 0.0.0.0:8005 --ipdb
