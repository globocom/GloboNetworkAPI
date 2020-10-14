#!/bin/sh

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_LOG_QUEUE=0

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

# Updates the SDN controller ip address
export REMOTE_CTRL_IP=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
echo "Found SDN controller at $REMOTE_CTRL_IP"

echo "Starting tests.."
python manage.py test app=networkapi/api_environment
python manage.py test app=networkapi/plugins/SDN
python manage.py test app=networkapi/api_ip
python manage.py test app=networkapi/api_network
python manage.py test app=networkapi/api_environment_vip
python manage.py test app=networkapi/api_asn
python manage.py test app=networkapi/api_interface
python manage.py test app=networkapi/api_list_config_bgp
python manage.py test app=networkapi/api_rack

