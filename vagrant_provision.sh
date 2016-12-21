#!/bin/bash

apt-get install vim -y
apt-get install memcached -y
apt-get install python-pip -y
apt-get install libmysqlclient-dev -y
apt-get install python-dev -y
apt-get install libldap2-dev libsasl2-dev libssl-dev -y
pip install -r /vagrant/requirements.txt

pip install gunicorn
#criar usuario  no DB
#load migrations
# externel access:
# mysql -uroot -hlocalhost -e 'GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION; FLUSH PRIVILEGES;'
# vim /etc/mysql/my.cnf
# change bind-address		= 127.0.0.1 to bind-address		= 0.0.0.0
mysql -uroot -hlocalhost -e 'drop database if exists networkapi;'
mysql -uroot -hlocalhost -e 'create database networkapi;'
cd /vagrant/dbmigrate; db-migrate --show-sql
#mysql -u root -h localhost < /vagrant/dev/database_configuration.sql
mysql -u root -h localhost networkapi < /vagrant/dev/load_example_environment.sql

echo -e "PYTHONPATH=\"/vagrant/networkapi:/vagrant/$PYTHONPATH\"" >> /etc/environment

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

/usr/local/bin/gunicorn -c /vagrant/gunicorn.conf.py networkapi_wsgi:application.
EOM

chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults
export PYTHONPATH="/vagrant/networkapi:/vagrant/$PYTHONPATH"

. /vagrant/start_networkapi.sh
