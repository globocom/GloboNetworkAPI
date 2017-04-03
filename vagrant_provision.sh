#!/bin/bash

apt-get install vim -y
apt-get install memcached -y
apt-get install python-pip -y
apt-get install libmysqlclient-dev -y
apt-get install python-dev -y
apt-get install libldap2-dev libsasl2-dev libssl-dev -y

# RabbitMQ
apt-get install rabbitmq-server -y
rabbitmq-plugins enable rabbitmq_management
rabbitmq-server restart &
rabbitmqctl add_user networkapi networkapi
rabbitmqctl add_vhost tasks
rabbitmqctl add_user tasks tasks
rabbitmqctl change_password networkapi networkapi
rabbitmqctl change_password tasks tasks
rabbitmqctl set_user_tags networkapi administrator
rabbitmqctl set_permissions -p / networkapi ".*" ".*" ".*"
rabbitmqctl set_permissions -p tasks networkapi ".*" ".*" ".*"
rabbitmqctl set_permissions -p tasks tasks ".*" ".*" ".*"

pip install gunicorn
pip install virtualenv virtualenvwrapper

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

/usr/local/bin/gunicorn -c /vagrant/gunicorn.conf.py networkapi_wsgi:application
EOM

chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults
export PYTHONPATH="/vagrant/networkapi:/vagrant/$PYTHONPATH"

cd /vagrant/
./start_networkapi.sh
source networkapi_venv/bin/activate

mysql -u root -h localhost -e 'drop database if exists networkapi;'
mysql -u root -h localhost -e 'create database networkapi;'
cd /vagrant/dbmigrate; db-migrate --show-sql
mysql -u root -h localhost networkapi < /vagrant/dev/load_example_environment.sql
