-- load_example_environment.sql	
--
-- Script for load into your database the environment used for documentation examples
--
-- Host: localhost    Database: networkapi
--
-- Current Database: `networkapi`
--
-- ----------------------------------------------------------------------------------


-- Dumping data for table `ambiente_logico`
INSERT INTO `ambiente_logico` VALUES
    (11,'AMBIENTE_LOGICO_RED'),
    (12,'AMBIENTE_LOGICO_BLUE'),
    (13,'AMBIENTE_LOGICO_GREEN'),
    (14,'AMBIENTE_LOGICO_YELLOW'),
    (15,'AMBIENTE_LOGICO_ORANGE');


-- Dumping data for table `divisao_dc`
INSERT INTO `divisao_dc` VALUES
    (21,'DIVISAO_DC_RED'),
    (22,'DIVISAO_DC_BLUE'),
    (23,'DIVISAO_DC_GREEN'),
    (24,'DIVISAO_DC_YELLOW'),
    (25,'DIVISAO_DC_ORANGE');


-- Dumping data for table `grupo_l3`
INSERT INTO `grupo_l3` VALUES
    (31,'GRUPO_L3_RED'),
    (32,'GRUPO_L3_BLUE'),
    (33,'GRUPO_L3_GREEN'),
    (34,'GRUPO_L3_YELLOW'),
    (35,'GRUPO_L3_ORANGE');


-- Dumping data for table `filter`
INSERT INTO `filter` VALUES (1,'Servidores','Servidores');


-- Dumping data for table `ambiente`
INSERT INTO `ambiente` (id_ambiente, id_grupo_l3, id_ambiente_logic, id_divisao, link, acl_path, ipv4_template, ipv6_template, id_filter, min_num_vlan_1, max_num_vlan_1, min_num_vlan_2, max_num_vlan_2) VALUES
    (1,31,11,21,' http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','Red',NULL,NULL,NULL,11,20, NULL, NULL),
    (2,32,12,22,'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','Blue',NULL,NULL,NULL,21,30, NULL, NULL),
    (3,33,13,23,'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','Green',NULL,NULL,NULL,31,31, NULL, NULL),
    (4,34,14,24,'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','Yellow',NULL,NULL,NULL,20,20, NULL, NULL),
    (5,35,15,25,' http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','Orange',NULL,NULL,NULL,15,19, NULL, NULL),
    (6,35,11,21,'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','Other Color',NULL,NULL,NULL,1,500,501,1000),
    (7,32,13,21,'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','NULL',NULL,NULL,NULL,15,19,NULL,NULL),
    (8,33,14,21,'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment','NULL',NULL,NULL,NULL,15,19,NULL,NULL),
    (9,33,11,21,'Equipment Environment Test','NULL',NULL,NULL,NULL,1,500,501,1000),
    (10,33,12,21,'Pool Environment Test','NULL',NULL,NULL,NULL,1,500,501,1000);


-- Dumping data for table `marcas`
INSERT INTO `marcas` VALUES (1,'MARCA');


-- Dumping data for table `tipo_equipamento`
INSERT INTO `tipo_equipamento` VALUES
    (1,'Switch'),
    (2,'Servidor'),
    (3,'Roteador'),
    (5,'Balanceador');


-- Dumping data for table `tipo_rede`
INSERT INTO `tipo_rede` VALUES
    (2,'Ponto a ponto'),
    (6,'Rede invalida equipamentos'),
    (7,'Rede invalida NAT'),
    (8,'Rede invalida VIP'),
    (9,'Rede valida equipamentos'),
    (10,'Rede valida NAT'),
    (11,'Rede valida VIP');


-- Dumping data for table `modelos`
INSERT INTO `modelos` VALUES (1,'MODELO',1);


-- Dumping data for table `ip_config`
INSERT INTO `ip_config` VALUES
    (1,'172.16.0.5/24','24','v4',2),
    (2,'10.0.0.5/24','24','v4',2),
    (3,'192.168.0.0/30','30','v4',2),
    (4,'192.168.1.0/30','30','v4',2),
    (5,'10.0.1.0/28','28','v4',2),

    (6,'10.237.128.0/18','28','v4',2),
    (7,'fdbe:bebe:bebe:1200:0:0:0:0/57','64','v6',2),
    (8,'192.168.104.0/22','27','v4',2),
    (9,'fdbe:bebe:bebe:11c0:0000:0000:0000:0000/58',64,'v6',2 );


-- Dumping data for table `ip_config`
INSERT INTO `config_do_ambiente` (id_config_do_ambiente, id_ambiente, id_ip_config) VALUES
    (1,6,6),
    (2,6,7),
    (3,9,6),
    (4,9,7),
    (5,10,8),
    (6,10,9);


-- Dumping data for table `vlans`
INSERT INTO `vlans` VALUES
    (1,'Vlan 31',31,3,'','',1,1,NULL,0, 1, NULL, NULL),
    (2,'Vlan 20',20,4,'','',1,1,NULL,0, 1, NULL, NULL),
    (3,'Vlan 11',11,1,'','',1,1,NULL,0, 1, NULL, NULL),
    (4,'Vlan 21',21,2,'','',1,1,NULL,0, 1, NULL, NULL),
    (5,'Vlan 22',22,2,'','',1,1,NULL,0, 1, NULL, NULL),
    (6,'Vlan 21',21,5,'','',1,1,NULL,0, 1, NULL, NULL),
    (7,'Vlan 15',15,5,'','',1,1,NULL,0, 1, NULL, NULL),
    (8,'Vlan Environment Equipment Test',1,9,'','',1,0,NULL,0, 1, NULL, NULL),
    (9,'Vlan Environment Pool Test',1,10,'','',1,0,NULL,0, 1, NULL, NULL);


-- Dumping data for table `equipamentos`
INSERT INTO `equipamentos` VALUES
    (1,1,1,'Switch R1', 0),
    (2,1,1,'Switch R2', 0),
    (3,1,1,'Switch R3', 0),
    (4,1,1,'Switch B1', 0),
    (5,1,1,'Switch B2', 0),
    (6,1,1,'Switch B3', 0),
    (7,1,1,'Switch 01', 0),
    (8,1,1,'Switch 02', 0),
    (9,1,1,'Switch 03', 0),
    (10,3,1,'SR1', 0),
    (11,3,1,'SR2', 0),
    (12,3,1,'Router', 0),
    (13,2,1,'Server S1', 0),
    (14,2,1,'Server P1',0),
    (15,2,1,'Server P2',0),
    (16,2,1,'Server P3',0),
    (17,5,1,'Load-Balancer', 0);


-- Dumping data for table `ambientevip`
INSERT INTO `ambientevip` VALUES
    (1,'Red','Red','Red', 'Red', NULL),
    (2,'Red','Blue','red', 'red', NULL),
    (3,'Red','Green','Red', 'Red', NULL),
    (4,'Red','Yellow','Red', 'Red', NULL),
    (5,'Red','Orange','Red', 'Red', NULL),
    (6,'Blue','Red','Red', 'Red', NULL),
    (7,'Blue','Blue','Red', 'Red', NULL),
    (8,'Blue','Blue','Blue', 'Blue', NULL),
    (9,'Green','Green','Green', 'Green', NULL),
    (10,'Yellow','Yellow','Yellow', 'Yellow', NULL),
    (11,'Orange','Orange','Orange', 'Orange', NULL),
    (12,'EnvironmentVIP NetworkAPI Test','Test','Test', 'Test', NULL);


-- Dumping data for table `redeipv4`
INSERT INTO `redeipv4` VALUES
    (1,1,192,168,0,0,30,255,255,255,0,2,'192.168.0.3',NULL,0, NULL),
    (2,2,192,168,1,0,30,255,255,255,0,2,'192.168.1.3',NULL,0, NULL),
    (3,4,172,16,0,5,24,255,255,255,0,2,'172.16.0.255',NULL,0, NULL),
    (4,7,10,0,0,5,30,255,255,255,0,2,'10.0.0.255',NULL,0, NULL),
    (5,8,10,237,128,0,28,255,255,255,240,2,'10.237.128.15',NULL,0,NULL),
    (6,9,192,168,104,0,27,255,255,255,224,2,'192.168.104.31', 12,0,NULL);

-- Dumping data for table `redeipv4`
INSERT INTO `redeipv6` VALUES
    (1, NULL,8,2,'fdbe','bebe','bebe','1200','0000','0000','0000','0000',64,'ffff','ffff','ffff','ffff','0000','0000','0000','0000',0,NULL),
    (2, 12 ,9,2,'fdbe','bebe','bebe','11c0','0000','0000','0000','0000',64,'ffff','ffff','ffff','ffff','0000','0000','0000','0000',0,NULL);


-- Dumping data for table `ips`
INSERT INTO `ips` VALUES
    (1,1,0,168,192,'SR1',1),
    (2,2,0,168,192,'Router',1),
    (3,1,1,168,192,'Router',2),
    (4,2,1,168,192,'SR2',2),
    (5,6,0,16,172,'Server S1',3),
    (6,6,0,0,10,'Server S1',4),
    (7,1,128, 237, 10,'Server P1', 5),
    (8,2,128, 237, 10,'Server P2', 5),
    (9,3,128, 237, 10,'Server P3', 5);


-- Dumping data for table `ips_dos_equipamentos`
INSERT INTO `ips_dos_equipamentos` VALUES
    (1,1,10),
    (2,2,12),
    (3,3,12),
    (4,4,11),
    (5,5,13),
    (6,6,13),
    (7,7,14),
    (8,8,15),
    (9,9,16);


-- Dumping data for table `ips`
INSERT INTO `ipsv6` VALUES
    (1,NULL,1,'fdbe','bebe','bebe','1200','0000','0000','0000','0001'),
    (2,NULL,1,'fdbe','bebe','bebe','1200','0000','0000','0000','0002'),
    (3,NULL,1,'fdbe','bebe','bebe','1200','0000','0000','0000','0003');


-- Dumping data for table `ips_dos_equipamentos`
INSERT INTO `ipsv6_dos_equipamentos` VALUES
    (1,1,14),
    (2,2,15),
    (3,3,16);


-- Dumping data for table `usuarios`
INSERT INTO `usuarios` (user, pwd, id_user, nome, ativo, email, user_ldap) VALUES
    ('networkapi', MD5('networkapi'), 1, 'Globo Network API test user', 1, 'networkapi@globo.com', NULL);

-- Dumping data for table `grupos`
INSERT INTO `grupos` (id, nome, leitura, escrita, edicao, exclusao) VALUES
    (1, 'Admin', 'S', 'S', 'S', 'S');

-- Dumping data for table `usuarios_do_grupo`
INSERT INTO `usuarios_do_grupo`
    (id_usuarios_do_grupo, id_user, id_grupo) VALUES
    (1, 1, 1);

-- Dumping data for table `permissions`
INSERT INTO `permissions` (id_permission, function) VALUES
    (1, 'administracao_usuarios'),
    (2, 'administrativa'),
    (3, 'cadastro_de_vlans'),
    (4, 'cadastro_de_ambiente'),
    (5, 'cadastro_de_equipamentos'),
    (6, 'opcao_vip'),
    (7, 'cadastro_de_pool'),
    (8, 'script_alterar_pool'),
    (9, 'script_criacao_pool'),
    (10, 'script_remover_pool'),
    (11, 'ips');


-- Dumping data for table `permissoes_administrativas`
INSERT INTO `permissoes_administrativas`
    (id_permissoes_administrativas, leitura, escrita, grupos_id,
     permission_id) VALUES
    (1, 1, 1, 1, 1),
    (2, 1, 1, 1, 2),
    (3, 1, 1, 1, 3),
    (4, 1, 1, 1, 4),
    (5, 1, 1, 1, 5),
    (6, 1, 1, 1, 6),
    (7, 1, 1, 1, 7),
    (8, 1, 1, 1, 8),
    (9, 1, 1, 1, 9),
    (10, 1, 1, 1, 10),
    (11, 1, 1, 1, 11);


-- Dumping data for table `grupos_equip`
INSERT INTO `grupos_equip` (id, nome) VALUES
    (1, 'Grupo de Equipamento Teste Network API');


-- Dumping data for table `equip_do_grupo`
INSERT INTO `equip_do_grupo` (id_equip_do_grupo, id_egrupo, id_equip) VALUES
    (1,1,1),
    (2,1,2),
    (3,1,3),
    (4,1,4),
    (5,1,5),
    (6,1,6),
    (7,1,7),
    (8,1,8),
    (9,1,9),
    (10,1,10),
    (11,1,11),
    (12,1,12),
    (13,1,13);


-- Dumping data for table `direitos_grupoequip`
INSERT INTO `direitos_grupoequip` (id_direito, id_ugrupo, id_egrupo, leitura, escrita, alterar_config, exclusao) VALUES
    (1,1,1,1,1,1,1);


-- Dumping data for table `vrf`
INSERT INTO `vrf` (id, internal_name, vrf) VALUES
    (1, 'default', 'default'),
    (2, 'Vrf-1', 'Vrf-1'),
    (3, 'Vrf-2', 'Vrf-2');


-- Dumping data for table `optionspool`
INSERT INTO `optionspool` (id_optionspool, type, description) VALUES
    (1, 'HealthCheck', 'TCP'),
    (2, 'HealthCheck', 'HTTP'),
    (3, 'HealthCheck', 'UDP'),
    (4, 'HealthCheck', 'HTTPS'),
    (5, 'ServiceDownAction', 'none'),
    (6, 'ServiceDownAction', 'drop'),
    (7, 'ServiceDownAction', 'reset'),
    (8, 'ServiceDownAction', 'reselect');


-- Dumping data for table `equip_do_ambiente`
INSERT INTO `equip_do_ambiente` (id_equip_do_ambiente, id_ambiente, id_equip, is_router) VALUES
    (1, 9, 14, 0),
    (2, 9, 15, 0),
    (3, 9, 16, 0),
    (4, 10, 17, 0);

-- Dumping data for table `environment_environment_vip`
INSERT INTO `environment_environment_vip` (id, environment_id, environment_vip_id) VALUES
    (1, 9, 12);

-- Dumping data for table `opcoesvip`
INSERT INTO `opcoesvip` (id, tipo_opcao, nome_opcao_txt) VALUES
    (1, 'Retorno de trafego', 'Normal'),
    (2, 'cache', 'CACHOS-DEV');


-- Dumping data for table `config`
INSERT INTO `config` (id_config, ip_v4_min, ip_v4_max, ip_v6_min, ip_v6_max) VALUES
    (1, 2, 3, 0, 0);

