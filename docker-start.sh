# Waits for other containers availability
sleep 5

mysql -uroot -h netapi_db -e 'drop database if exists networkapi;'
mysql -uroot -h netapi_db -e 'create database networkapi;'
cd /netapi/dbmigrate; db-migrate --show-sql
mysql -u root -h netapi_db networkapi < /netapi/dev/load_example_environment.sql

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
/usr/local/bin/gunicorn -c /netapi/gunicorn.conf.py networkapi_wsgi:application

tail -f /tmp/gunicorn-networkapi_error.log
