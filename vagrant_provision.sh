#!/bin/bash

apt-get install vim -y
apt-get install memcached -y
apt-get install python-pip -y
apt-get install libmysqlclient-dev -y
apt-get install python-dev -y
apt-get install libldap2-dev libsasl2-dev libssl-dev -y
apt-get install activemq -y
rm -rf /etc/activemq/instances-enabled
ln -sf /etc/activemq/instances-available /etc/activemq/instances-enabled
sed 's/512/128/g' /usr/share/activemq/activemq-options
sed -i 's/.*openwire.*/\t\t<transportConnector name="stomp" uri="stomp:\/\/localhost:61613"\/>/g' /etc/activemq/instances-available/main/activemq.xml

pip install -r /vagrant/requirements.txt

pip install gunicorn
#criar usuario  no DB
#load migrations
# externel access:
# mysql -uroot -hlocalhost -e 'GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION; FLUSH PRIVILEGES;'
# vim /etc/mysql/my.cnf
# change bind-address		= 127.0.0.1 to bind-address		= 0.0.0.0
mysql -u root -h localhost -e 'drop database if exists networkapi;'
mysql -u root -h localhost -e 'create database networkapi;'
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
