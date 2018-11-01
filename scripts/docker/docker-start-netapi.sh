#
# Script to run Network API on a docker container
#



# Time to sleep before retrying to talk to database container
SLEEP_TIME=5

# Maximum number of retries on database container
MAX_RETRIES=30

# Network API pid file path
PIDFILE=/var/run/netapi_main.pid

# Control variable to check if the database container is ready
DB_READY=0




#
# Script begin
#
echo "Starting netapi_app ..."


# Waits for database container to be ready
for i in $(seq 1  ${MAX_RETRIES}); do

  mysql -u root -h netapi_db -e 'DROP DATABASE IF EXISTS networkapi;'

  if [ "$?" -eq "0" ]; then
    echo "Dropping old networkapi database"
    DB_READY=1;
    break;
  fi

  echo "DB not ready. Trying again in ${SLEEP_TIME} seconds."
  sleep ${SLEEP_TIME}
  echo "Retrying ${i}.."
done


# Exits if we can not connect to database container
if [ "$DB_READY" -eq "0" ]; then
  echo "Fatal error: Could not connect to DB"
  exit 1;
fi



echo "Creating networkapi database"
mysql -u root -h netapi_db -e 'CREATE DATABASE IF NOT EXISTS networkapi;'


# Running database migrations if exists
cd /netapi/dbmigrate; db-migrate --show-sql


echo "Loading base Network API data into database"
mysql -u root -h netapi_db networkapi < /netapi/dev/load_example_environment.sql


# Updates the SDN controller ip address
echo "Configuring ODL container's host address if exists"
REMOTE_CTRL=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
echo "$REMOTE_CTRL  odl.controller" >> /etc/hosts


# Adds project root directory to Python path
echo -e "PYTHONPATH=\"/netapi/networkapi:/netapi/$PYTHONPATH\"" >> /etc/environment
export PYTHONPATH="/netapi/networkapi:/netapi/$PYTHONPATH"


# Creates System V init script
# TODO: We should move to System D or Supervisor D
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

/usr/local/bin/gunicorn --pid $PIDFILE -c /netapi/gunicorn.conf.py wsgi:application
EOM


# Enable the init script
chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults


echo "Starting gunicorn"
cd /netapi
touch /tmp/gunicorn-networkapi_error.log
/etc/init.d/gunicorn_networkapi

tail -f /tmp/gunicorn-networkapi_error.log
