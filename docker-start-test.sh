export NETWORKAPI_DEBUG=DEBUG
export CI=1
export NETWORKAPI_DATABASE_OPTIONS='{"init_command": "SET default_storage_engine=INNODB"}'
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'
export REMOTE_CTRL_IP=netapi_odl
python manage.py jenkins "$@"
