
mysql -uroot -h netapi_db -e 'drop database if exists networkapi;'
mysql -uroot -h netapi_db -e 'create database networkapi;'
cd /netapi/dbmigrate; db-migrate --show-sql
mysql -u root -h netapi_db networkapi < /netapi/dev/load_example_environment.sql


echo -e "PYTHONPATH=\"/netapi/networkapi:/netapi/$PYTHONPATH\"" >> /etc/environment
echo -e '#!/bin/bash\n/usr/local/bin/gunicorn -c /netapi/gunicorn.conf.py networkapi_wsgi:application' > /etc/init.d/gunicorn_networkapi
chmod 777 /etc/init.d/gunicorn_networkapi
update-rc.d gunicorn_networkapi defaults

export PYTHONPATH="/netapi/networkapi:/netapi/$PYTHONPATH"
/usr/local/bin/gunicorn  -c /netapi/gunicorn.conf.py networkapi_wsgi:application
