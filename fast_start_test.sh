#!/bin/sh

pip install -r requirements_test.txt

echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_LOG_QUEUE=0

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

# Updates the SDN controller ip address
export REMOTE_CTRL_IP=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
echo "Found SDN controller at $REMOTE_CTRL_IP"

echo "Starting tests.."
echo "=============== Tests for IPV4 ================="
python manage.py test networkapi/api_ip/tests/sanity/ipv4/sync/test_delete.py
python manage.py test networkapi/api_ip/tests/sanity/ipv4/sync/test_get.py
python manage.py test networkapi/api_ip/tests/sanity/ipv4/sync/test_post.py
python manage.py test networkapi/api_ip/tests/sanity/ipv4/sync/test_put.py
python manage.py test networkapi/api_ip/tests/unit/ipv4/async/test_delete.py
python manage.py test networkapi/api_ip/tests/unit/ipv4/async/test_post.py
python manage.py test networkapi/api_ip/tests/unit/ipv4/async/test_put.py
python manage.py test networkapi/api_ip/tests/sanity/ipv4/async/test_put.py
python manage.py test networkapi/api_ip/v4/tests/unity/ipv4/async/test_delete.py
python manage.py test networkapi/api_ip/v4/tests/unity/ipv4/async/test_post.py
python manage.py test networkapi/api_ip/v4/tests/unity/ipv4/async/test_put.py
