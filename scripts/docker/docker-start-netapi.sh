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

  mysql -u root -h ${NETWORKAPI_DATABASE_HOST} -e 'DROP DATABASE IF EXISTS networkapi;'

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
mysql -u root -h ${NETWORKAPI_DATABASE_HOST} -e 'CREATE DATABASE IF NOT EXISTS networkapi;'


# Running database migrations if exists
cd /netapi/dbmigrate; db-migrate --show-sql


echo "Loading base Network API data into database"
mysql -u root -h ${NETWORKAPI_DATABASE_HOST} networkapi < /netapi/dev/load_example_environment.sql


# Discovering SDN controller
REMOTE_CTRL=$(nslookup ${NETWORKAPI_SDN_CTRL} | grep Address | tail -1 | awk '{print $2}')
echo "$REMOTE_CTRL  odl.controller" >> /etc/hosts
echo "Found SDN controller: ${REMOTE_CTRL}"



echo "Starting gunicorn using supervisord"
/venv/bin/supervisord -c /netapi/scripts/docker/netapi_supervisord.conf
/venv/bin/supervisorctl tail -f netapi stdout
