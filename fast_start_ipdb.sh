#!/bin/bash
export NETWORKAPI_PDB=1 
python manage.py clean_pyc --path /vagrant/networkapi/
python manage.py runserver 0.0.0.0:8005 --ipdb

