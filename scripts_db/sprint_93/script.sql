
CREATE TABLE environment_environment_vip (
    id int not null auto_increment,
    environment_id int(10) unsigned not null,
    environment_vip_id int(10) unsigned not null,
    primary key (id),
    constraint environment_fk foreign key (environment_id) references ambiente(id_ambiente),
    constraint environment_vip_fk foreign key (environment_vip_id) references ambientevip(id)
);