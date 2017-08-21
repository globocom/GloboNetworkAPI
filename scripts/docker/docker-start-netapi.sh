# initial vars
SLEEP_TIME=5
MAX_RETRIES=10
PIDFILE=/var/run/netapi_main.pid

echo "Starting netapi_app ..."

# DB
for i in $(seq 1  ${MAX_RETRY}); do

  mysql -u root -h netapi_db -e 'DROP DATABASE IF EXISTS networkapi;'

  if [ "$?" -eq "0" ]; then
    echo "Dropping old networkapi database"
    break;
  fi

  echo "DB not ready. I'll try again in ${SLEEP_TIME} seconds."
  sleep ${SLEEP_TIME}
  echo "Retrying ${i}.."
done

echo "Creating networkapi database"
mysql -u root -h netapi_db -e 'CREATE DATABASE IF NOT EXISTS networkapi;'
cd /netapi/dbmigrate; db-migrate --show-sql
echo "Loading example environment into database"
mysql -u root -h netapi_db networkapi < /netapi/dev/load_example_environment.sql

# Updates the SDN controller ip address
echo "Configuring ODL container's host address"
REMOTE_CTRL=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
echo "$REMOTE_CTRL  odl.controller" >> /etc/hosts

echo -e "PYTHONPATH=\"/netapi/networkapi:/netapi/$PYTHONPATH\"" >> /etc/environment

cat > /etc/init.d/gunicorn_networkapi <<- EOM
#!/bin/bash
### BEGIN INIT INFO
# Provides:          scriptname
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

/usr/local/bin/gunicorn --pid $PIDFILE -c /netapi/gunicorn.conf.py networkapi_wsgi:application
EOM

chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults
export PYTHONPATH="/netapi/networkapi:/netapi/$PYTHONPATH"

echo "starting gunicorn"
/etc/init.d/gunicorn_networkapi

touch /tmp/gunicorn-networkapi_error.log
tail -f /tmp/gunicorn-networkapi_error.log

