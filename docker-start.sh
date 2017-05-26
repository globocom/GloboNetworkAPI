# Waits for other containers availability
sleep 5

mysql -u root -h netapi_db -e 'DROP DATABASE IF EXISTS networkapi;'
mysql -u root -h netapi_db -e 'CREATE DATABASE IF NOT EXISTS networkapi;'

cd /netapi/dbmigrate; db-migrate --show-sql
mysql -u root -h netapi_db networkapi < /netapi/dev/load_example_environment.sql

# Updates the SDN controller ip address
REMOTE_CTRL=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
mysql -uroot -h netapi_db -b networkapi -e "UPDATE equiptos_access SET fqdn = 'http://${REMOTE_CTRL}:8181' WHERE id_equiptos_access = 1;"

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

/usr/local/bin/gunicorn -c /netapi/gunicorn.conf.py networkapi_wsgi:application
EOM

chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults
export PYTHONPATH="/netapi/networkapi:/netapi/$PYTHONPATH"

echo "starting gunicorn"
/usr/local/bin/gunicorn -c /netapi/gunicorn.conf.py networkapi_wsgi:application --reload

touch /tmp/gunicorn-networkapi_error.log
tail -f /tmp/gunicorn-networkapi_error.log
