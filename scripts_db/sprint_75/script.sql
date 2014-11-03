CREATE TABLE `opcoespool` (
  `id_opcaopool` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id_opcaopool`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO opcoespool (description) 
SELECT nome_opcao_txt FROM telecom.opcoesvip where tipo_opcao = 'HealthCheck';

CREATE TABLE `opcoespool_ambiente` (
  `id_opcaopool_ambiente` int(11) NOT NULL AUTO_INCREMENT,
  `id_opcaopool` int(11) NOT NULL,
  `id_ambiente` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id_opcaopool_ambiente`),
  KEY `fk_opcoes_id_opcaopool_idx` (`id_opcaopool`),
  KEY `fk_opcoes_id_ambiente_idx` (`id_ambiente`),
  CONSTRAINT `fk_opcoes_id_opcaopool` FOREIGN KEY (`id_opcaopool`) REFERENCES `opcoespool` (`id_opcaopool`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_opcoes_id_ambiente` FOREIGN KEY (`id_ambiente`) REFERENCES `ambiente` (`id_ambiente`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO opcoespool_ambiente (id_ambiente, id_opcaopool) 
SELECT vlans.id_ambiente, opcoespool.id_opcaopool  
FROM opcoesvip_ambiente_xref
INNER JOIN ambientevip ON ambientevip.id = opcoesvip_ambiente_xref.id_ambiente
INNER JOIN redeipv4 ON redeipv4.id_ambientevip = ambientevip.id
INNER JOIN vlans ON vlans.id_vlan = redeipv4.id_vlan
INNER JOIN opcoesvip ON opcoesvip_ambiente_xref.id_opcoesvip = opcoesvip.id
INNER JOIN opcoespool ON opcoesvip.nome_opcao_txt = opcoespool.description
WHERE opcoesvip.tipo_opcao = 'HealthCheck';

CREATE TABLE `healthcheckexpect_healthcheck` (
  `id_healthcheck` int(11) NOT NULL AUTO_INCREMENT,
  `identifier` varchar(200) NOT NULL,
  `healthcheck_type` varchar(45) NOT NULL,
  `healthcheck_request` varchar(500) NOT NULL,
  `healthcheck_expect` varchar(200) NOT NULL,
  `destination` varchar(45) NOT NULL,
  PRIMARY KEY (`id_healthcheck`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `config_do_ambiente` DROP INDEX `uniq_ip_config_ambiente` ;
ALTER TABLE `config_do_ambiente` ADD INDEX `unique_ip_config_ambiente` (`id_ambiente` ASC, `id_ip_config` ASC) ;

ALTER TABLE `ip_config` ADD COLUMN `network_type` INT UNSIGNED NULL  AFTER `type` ,
  ADD CONSTRAINT `fk_ip_config_tipo_rede`
  FOREIGN KEY (`network_type` )
  REFERENCES `tipo_rede` (`id_tipo_rede` )
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
, ADD INDEX `fk_ip_config_tipo_rede` (`network_type` ASC) ;

ALTER TABLE `equipamentos` CHANGE COLUMN nome nome varchar(50) NOT NULL;
ALTER TABLE `ambientevip` ADD COLUMN `description` CHAR(50) NOT NULL  AFTER `ambiente_p44_txt` ;

ALTER TABLE `server_pool` ADD COLUMN `ambiente_id_ambiente` INT UNSIGNED NULL  AFTER `default_port` , ADD COLUMN `pool_criado` TINYINT NOT NULL DEFAULT 0  AFTER `ambiente_id_ambiente` , ADD COLUMN `lb_method` VARCHAR(50) NULL  AFTER `pool_criado` , 
  ADD CONSTRAINT `fk_server_pool_environment`
  FOREIGN KEY (`ambiente_id_ambiente` )
  REFERENCES `ambiente` (`id_ambiente` )
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
, ADD INDEX `fk_server_pool_environment` (`ambiente_id_ambiente` ASC) ;

ALTER TABLE `server_pool` 
DROP INDEX `fk_server_pool_environment` 
, ADD INDEX `fk_server_pool_environment` (`ambiente_id_ambiente` ASC, `identifier` ASC) ;


UPDATE `server_pool` as sp
SET `ambiente_id_ambiente`= (
SELECT `ambiente`.`id_ambiente` 
FROM `ambiente` 
INNER JOIN `vlans` ON (`ambiente`.`id_ambiente` = `vlans`.`id_ambiente`) 
LEFT OUTER JOIN `redeipv4` ON (`vlans`.`id_vlan` = `redeipv4`.`id_vlan`) 
LEFT OUTER JOIN `ips` ON (`redeipv4`.`id` = `ips`.`id_redeipv4`) 
LEFT OUTER JOIN `requisicao_vips` ON (`ips`.`id_ip` = `requisicao_vips`.`ips_id_ip`) 
LEFT OUTER JOIN `vip_port_to_pool` ON (`requisicao_vips`.`id_requisicao_vips` = `vip_port_to_pool`.`id_requisicao_vips`) 
LEFT OUTER JOIN `redeipv6` ON (`vlans`.`id_vlan` = `redeipv6`.`id_vlan`) 
LEFT OUTER JOIN `ipsv6` ON (`redeipv6`.`id` = `ipsv6`.`id_redeipv6`) 
LEFT OUTER JOIN `requisicao_vips` T10 ON (`ipsv6`.`id_ipv6` = T10.`ipsv6_id_ipv6`) 
LEFT OUTER JOIN `vip_port_to_pool` T11 ON (T10.`id_requisicao_vips` = T11.`id_requisicao_vips`) 
WHERE (`vip_port_to_pool`.`id_server_pool` = sp.`id_server_pool`  OR T11.`id_server_pool` = sp.`id_server_pool` ) LIMIT 1 )
WHERE `ambiente_id_ambiente` is null;


UPDATE server_pool sp, vip_port_to_pool vptp, requisicao_vips rv SET sp.pool_criado = rv.vip_criado WHERE sp.id_server_pool = vptp.id_server_pool AND vptp.id_requisicao_vips = rv.id_requisicao_vips;


INSERT INTO `permissions` (`function`) VALUES ('cadastro_de_pool');
INSERT INTO `permissions` (`function`) VALUES ('script_remover_pool');
INSERT INTO `permissions` (`function`) VALUES ('script_criacao_pool');
INSERT INTO `permissions` (`function`) VALUES ('script_alterar_pool');

