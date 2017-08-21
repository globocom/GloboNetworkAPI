#!/bin/bash -e

dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
$dir/wait_for_containers.sh

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_DEBUG='DEBUG'

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

echo "Starting tests.."
python manage.py test "$@"
