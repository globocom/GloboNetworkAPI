#!/bin/bash

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_DEBUG='DEBUG'

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

echo "Starting tests.."
python manage.py test "$@"
