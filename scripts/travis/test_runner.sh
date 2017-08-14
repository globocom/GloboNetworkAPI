#!/bin/bash
if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

source test_venv/bin/activate

# Database configuration
mysql -u root -h localhost -e 'DROP DATABASE IF EXISTS networkapi;'
mysql -u root -h localhost -e 'CREATE DATABASE IF NOT EXISTS networkapi;'

cd dbmigrate
db-migrate --show-sql
cd ..

mysql -u root -h localhost networkapi < dev/load_example_environment.sql

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_DEBUG='DEBUG'

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

echo "Starting tests.."
python manage.py test "$@"
