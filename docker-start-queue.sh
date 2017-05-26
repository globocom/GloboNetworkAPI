rabbitmq-plugins enable rabbitmq_management
rabbitmqctl add_user networkapi networkapi
rabbitmqctl add_vhost tasks
rabbitmqctl add_user tasks tasks
rabbitmqctl change_password networkapi networkapi
rabbitmqctl change_password tasks tasks
rabbitmqctl set_user_tags networkapi administrator
rabbitmqctl set_permissions -p / networkapi ".*" ".*" ".*"
rabbitmqctl set_permissions -p tasks networkapi ".*" ".*" ".*"
rabbitmqctl set_permissions -p tasks tasks ".*" ".*" ".*"
