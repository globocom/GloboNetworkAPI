#!/bin/sh

pip install supervisor

echo "Wait rabbitMQ to start.."
sleep 10;

export NETWORKAPI_BROKER_URL=netapi_queue

echo "Starting Celery through supervisord"
/usr/local/bin/supervisord  -c supervisord.conf

echo "Logging.."
/usr/local/bin/supervisorctl tail -f celeryd
