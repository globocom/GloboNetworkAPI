CREATE TABLE `optionspool` (
  `id_optionspool` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(200) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id_optionspool`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO optionspool (type,description)
SELECT tipo_opcao, nome_opcao_txt FROM telecom.opcoesvip where tipo_opcao = 'HealthCheck';

INSERT INTO optionspool (type,description) values ('HealthCheck', 'HTTPS');
INSERT INTO optionspool (type,description) values ('ServiceDownAction', 'none');
INSERT INTO optionspool (type,description) values ('ServiceDownAction', 'drop');
INSERT INTO optionspool (type,description) values ('ServiceDownAction', 'reset');
INSERT INTO optionspool (type,description) values ('ServiceDownAction', 'reselect');





CREATE TABLE `optionspool_environment_xref` (
  `id_optionspool_environment_xref` int(11) NOT NULL AUTO_INCREMENT,
  `id_optionspool` int(11) NOT NULL,
  `id_environment` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id_optionspool_environment_xref`),
  KEY `fk_options_id_optionspool_idx` (`id_optionspool`),
  KEY `fk_options_id_environment_idx` (`id_environment`),
  CONSTRAINT `fk_options_id_optionspool` FOREIGN KEY (`id_optionspool`) REFERENCES `optionspool` (`id_optionspool`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_options_id_environment` FOREIGN KEY (`id_environment`) REFERENCES `ambiente` (`id_ambiente`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO optionspool_environment_xref (id_environment, id_optionspool)
SELECT distinct vlans.id_ambiente, optionspool.id_optionspool
FROM opcoesvip_ambiente_xref
INNER JOIN ambientevip ON ambientevip.id = opcoesvip_ambiente_xref.id_ambiente
INNER JOIN redeipv4 ON redeipv4.id_ambientevip = ambientevip.id
INNER JOIN vlans ON vlans.id_vlan = redeipv4.id_vlan
INNER JOIN opcoesvip ON opcoesvip_ambiente_xref.id_opcoesvip = opcoesvip.id
INNER JOIN optionspool ON opcoesvip.nome_opcao_txt = optionspool.description
WHERE opcoesvip.tipo_opcao = 'HealthCheck' ; 

INSERT INTO optionspool_environment_xref (id_environment, id_optionspool)
SELECT distinct vlans.id_ambiente, 4
FROM opcoesvip_ambiente_xref
INNER JOIN ambientevip ON ambientevip.id = opcoesvip_ambiente_xref.id_ambiente
INNER JOIN redeipv4 ON redeipv4.id_ambientevip = ambientevip.id
INNER JOIN vlans ON vlans.id_vlan = redeipv4.id_vlan
INNER JOIN opcoesvip ON opcoesvip_ambiente_xref.id_opcoesvip = opcoesvip.id
INNER JOIN optionspool ON opcoesvip.nome_opcao_txt = optionspool.description
WHERE opcoesvip.tipo_opcao = 'HealthCheck' and 
optionspool.id_optionspool = '1' ;




ALTER TABLE `server_pool` ADD COLUMN `service-down-action_id` INT(11) DEFAULT 5  AFTER `healthcheck_id_healthcheck` ; 








