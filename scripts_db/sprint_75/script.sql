CREATE TABLE `opcoes_pool` (
  `id_opcao_pool` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id_opcao_pool`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `opcoes_pool_ambiente` (
  `id_opcao_pool_ambiente` int(11) NOT NULL AUTO_INCREMENT,
  `id_opcao_pool` int(11) NOT NULL,
  `id_ambiente` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id_opcao_pool_ambiente`),
  KEY `fk_opcoes_id_opcao_pool_idx` (`id_opcao_pool`),
  KEY `fk_opcoes_id_ambiente_idx` (`id_ambiente`),
  CONSTRAINT `fk_opcoes_id_opcao_pool` FOREIGN KEY (`id_opcao_pool`) REFERENCES `opcoes_pool` (`id_opcao_pool`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_opcoes_id_ambiente` FOREIGN KEY (`id_ambiente`) REFERENCES `ambiente` (`id_ambiente`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

