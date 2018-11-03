#!/bin/sh

pip install supervisor

echo "Wait rabbitMQ to start.."
sleep 10;

export NETWORKAPI_BROKER_URL=netapi_queue

echo "Starting Celery through supervisord"
touch /tmp/celeryd.log
/venv/bin/supervisord -c scripts/docker/supervisord.conf
/venv/bin/supervisorctl tail -f celeryd
