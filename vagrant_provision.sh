apt-get install memcached -y
apt-get install python-pip -y
apt-get install libmysqlclient-dev -y
apt-get install python-dev -y
pip install -r /vagrant/requirements.txt
pip install gunicorn
#criar usuario  no DB
mysql -u root -ppassword -h localhost < /vagrant/dev/database_configuration.sql
mysql -u root -ppassword -h localhost telecom < /vagrant/dev/load_example_environment.sql

echo -e "PYTHONPATH=\"/vagrant/networkapi:/vagrant/$PYTHONPATH\"" >> /etc/environment
echo -e '#!/bin/bash\n/usr/local/bin/gunicorn -c /vagrant/gunicorn.conf.py networkapi_wsgi:application' > /etc/init.d/gunicorn_networkapi
chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults
export PYTHONPATH="/vagrant/networkapi:/vagrant/$PYTHONPATH"
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py networkapi_wsgi:application

