SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `telecom` DEFAULT CHARACTER SET utf8 ;
USE `telecom` ;

-- -----------------------------------------------------
-- Table `telecom`.`ambiente_logico`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ambiente_logico` (
  `id_ambiente_logic` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(80) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_ambiente_logic`),
  UNIQUE INDEX `nome` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Separação de ambiente utilizada na Globo.com';


-- -----------------------------------------------------
-- Table `telecom`.`divisao_dc`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`divisao_dc` (
  `id_divisao` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_divisao`),
  UNIQUE INDEX `nome` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Divisao da rede (FE, BE, Parceiros etc)';


-- -----------------------------------------------------
-- Table `telecom`.`filter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`filter` (
  `id_filter` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` VARCHAR(200) NULL DEFAULT '',
  PRIMARY KEY (`id_filter`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`grupo_l3`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`grupo_l3` (
  `id_grupo_l3` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(80) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_grupo_l3`),
  UNIQUE INDEX `nome` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Descreve grupo de roteamento de um ambiente';


-- -----------------------------------------------------
-- Table `telecom`.`ambiente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ambiente` (
  `id_ambiente` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_grupo_l3` INT(10) UNSIGNED NOT NULL,
  `id_ambiente_logic` INT(10) UNSIGNED NOT NULL,
  `id_divisao` INT(10) UNSIGNED NOT NULL,
  `link` VARCHAR(200) CHARACTER SET 'latin1' NULL DEFAULT 'http://wiki.globoi.com/DataCenter/Telecom',
  `acl_path` VARCHAR(250) NULL DEFAULT NULL,
  `ipv4_template` VARCHAR(250) NULL DEFAULT NULL,
  `ipv6_template` VARCHAR(250) NULL DEFAULT NULL,
  `id_filter` INT(10) UNSIGNED NULL DEFAULT NULL,
  `min_num_vlan_1` INT(10) NULL DEFAULT NULL,
  `max_num_vlan_1` INT(10) NULL DEFAULT NULL,
  `min_num_vlan_2` INT(10) NULL DEFAULT NULL,
  `max_num_vlan_2` INT(10) NULL DEFAULT NULL,
  PRIMARY KEY (`id_ambiente`),
  UNIQUE INDEX `ambiente_unico` (`id_grupo_l3` ASC, `id_ambiente_logic` ASC, `id_divisao` ASC),
  INDEX `fk_ambiente_ambiente_logico` (`id_ambiente_logic` ASC),
  INDEX `fk_ambiente_divisao_dc` (`id_divisao` ASC),
  INDEX `fk_ambiente_grupo_l3` (`id_grupo_l3` ASC),
  INDEX `fk_ambiente_filter` (`id_filter` ASC),
  CONSTRAINT `fk_ambiente_ambiente_logico`
    FOREIGN KEY (`id_ambiente_logic`)
    REFERENCES `telecom`.`ambiente_logico` (`id_ambiente_logic`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_ambiente_divisao_dc`
    FOREIGN KEY (`id_divisao`)
    REFERENCES `telecom`.`divisao_dc` (`id_divisao`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_ambiente_filter`
    FOREIGN KEY (`id_filter`)
    REFERENCES `telecom`.`filter` (`id_filter`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ambiente_grupo_l3`
    FOREIGN KEY (`id_grupo_l3`)
    REFERENCES `telecom`.`grupo_l3` (`id_grupo_l3`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`ambientevip`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ambientevip` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `finalidade_txt` CHAR(50) CHARACTER SET 'latin1' NOT NULL,
  `cliente_txt` CHAR(50) CHARACTER SET 'latin1' NOT NULL,
  `ambiente_p44_txt` CHAR(50) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`block_rules`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`block_rules` (
  `id_block_rules` INT(10) NOT NULL AUTO_INCREMENT,
  `content` TEXT NOT NULL,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `order` INT(10) NOT NULL,
  PRIMARY KEY (`id_block_rules`),
  INDEX `fk_block_rules_ambiente_idx` (`id_ambiente` ASC),
  CONSTRAINT `fk_block_rules_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambiente` (`id_ambiente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`config`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`config` (
  `id_config` TINYINT(4) NOT NULL,
  `ip_v4_min` TINYINT(4) NOT NULL,
  `ip_v4_max` TINYINT(4) NOT NULL,
  `ip_v6_min` TINYINT(4) NOT NULL,
  `ip_v6_max` TINYINT(4) NOT NULL,
  PRIMARY KEY (`id_config`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`tipo_rede`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`tipo_rede` (
  `id_tipo_rede` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `tipo_rede` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_tipo_rede`),
  UNIQUE INDEX `tipo_rede_unico` (`tipo_rede` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Informa o tipo dos IPs da vlan.';


-- -----------------------------------------------------
-- Table `telecom`.`ip_config`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ip_config` (
  `id_ip_config` INT(10) NOT NULL AUTO_INCREMENT,
  `subnet` VARCHAR(45) NOT NULL,
  `new_prefix` VARCHAR(3) NOT NULL,
  `type` ENUM('v6','v4') NOT NULL,
  `network_type` INT(10) UNSIGNED NULL DEFAULT NULL,
  PRIMARY KEY (`id_ip_config`),
  INDEX `fk_ip_config_1_idx` (`network_type` ASC),
  CONSTRAINT `fk_ip_config_network_type`
    FOREIGN KEY (`network_type`)
    REFERENCES `telecom`.`tipo_rede` (`id_tipo_rede`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`config_do_ambiente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`config_do_ambiente` (
  `id_config_do_ambiente` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `id_ip_config` INT(10) NOT NULL,
  PRIMARY KEY (`id_config_do_ambiente`),
  UNIQUE INDEX `ambiente_ip_config_unique` (`id_ambiente` ASC, `id_ip_config` ASC),
  INDEX `fk_config_do_ambiente_ambiente` (`id_ambiente` ASC),
  INDEX `fk_config_do_ambiente_ip_config` (`id_ip_config` ASC),
  CONSTRAINT `fk_config_do_ambiente_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambiente` (`id_ambiente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_config_do_ambiente_ip_config`
    FOREIGN KEY (`id_ip_config`)
    REFERENCES `telecom`.`ip_config` (`id_ip_config`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`grupos_equip`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`grupos_equip` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL COMMENT 'unique',
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`grupos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`grupos` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL COMMENT 'unique',
  `leitura` CHAR(1) NOT NULL,
  `escrita` CHAR(1) NOT NULL,
  `edicao` CHAR(1) NOT NULL,
  `exclusao` CHAR(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `nome` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`direitos_grupoequip`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`direitos_grupoequip` (
  `id_direito` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ugrupo` INT(10) UNSIGNED NOT NULL,
  `id_egrupo` INT(10) UNSIGNED NOT NULL,
  `leitura` CHAR(1) NOT NULL,
  `escrita` CHAR(1) NOT NULL,
  `alterar_config` CHAR(1) NOT NULL,
  `exclusao` CHAR(1) NOT NULL,
  PRIMARY KEY (`id_direito`),
  UNIQUE INDEX `uniq_ugrupo_egrupo` (`id_ugrupo` ASC, `id_egrupo` ASC),
  INDEX `fk_direitosg_ugrupos` (`id_ugrupo` ASC),
  INDEX `fk_direitosg_gequip` (`id_egrupo` ASC),
  CONSTRAINT `fk_direitosg_gequip`
    FOREIGN KEY (`id_egrupo`)
    REFERENCES `telecom`.`grupos_equip` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_direitosg_ugrupos`
    FOREIGN KEY (`id_ugrupo`)
    REFERENCES `telecom`.`grupos` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`marcas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`marcas` (
  `id_marca` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_marca`),
  UNIQUE INDEX `marca_unica` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Marca do equipamento (Cisco, 3Com etc...)';


-- -----------------------------------------------------
-- Table `telecom`.`modelos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`modelos` (
  `id_modelo` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL,
  `id_marca` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_modelo`),
  UNIQUE INDEX `modelo_marca_unicos` (`nome` ASC, `id_marca` ASC),
  INDEX `fk_modelos_marcas` (`id_marca` ASC),
  CONSTRAINT `fk_modelos_marcas`
    FOREIGN KEY (`id_marca`)
    REFERENCES `telecom`.`marcas` (`id_marca`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Modelo do equipamento';


-- -----------------------------------------------------
-- Table `telecom`.`tipo_equipamento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`tipo_equipamento` (
  `id_tipo_equipamento` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `tipo_equipamento` VARCHAR(100) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_tipo_equipamento`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Tipo do equipamento (roteador, servidor, switch)';


-- -----------------------------------------------------
-- Table `telecom`.`equipamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`equipamentos` (
  `id_equip` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_tipo_equipamento` INT(10) UNSIGNED NOT NULL,
  `id_modelo` INT(10) UNSIGNED NOT NULL DEFAULT '1',
  `nome` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_equip`),
  UNIQUE INDEX `nome` (`nome` ASC),
  INDEX `fk_equipamentos_tipo_equipamento` (`id_tipo_equipamento` ASC),
  INDEX `fk_equipamentos_modelos` (`id_modelo` ASC),
  CONSTRAINT `fk_equipamentos_modelos`
    FOREIGN KEY (`id_modelo`)
    REFERENCES `telecom`.`modelos` (`id_modelo`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_equipamentos_tipo_equipamento`
    FOREIGN KEY (`id_tipo_equipamento`)
    REFERENCES `telecom`.`tipo_equipamento` (`id_tipo_equipamento`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`equip_do_ambiente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`equip_do_ambiente` (
  `id_equip_do_ambiente` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `id_equip` INT(10) UNSIGNED NOT NULL,
  `is_router` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_equip_do_ambiente`),
  UNIQUE INDEX `uniq_id_ambiente_id_equip` (`id_equip` ASC, `id_ambiente` ASC),
  INDEX `fk_equip_do_ambiente_ambiente` (`id_ambiente` ASC),
  INDEX `fk_equip_do_ambiente_equipamentos` (`id_equip` ASC),
  CONSTRAINT `fk_equip_do_ambiente_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambiente` (`id_ambiente`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_equip_do_ambiente_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`equip_do_grupo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`equip_do_grupo` (
  `id_equip_do_grupo` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_egrupo` INT(10) UNSIGNED NOT NULL,
  `id_equip` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_equip_do_grupo`),
  UNIQUE INDEX `uniq_id_egrupo_ud_equip` (`id_egrupo` ASC, `id_equip` ASC),
  INDEX `fk_equip_do_grupo_grupo` (`id_egrupo` ASC),
  INDEX `fk_equip_do_grupo_equipamentos` (`id_equip` ASC),
  CONSTRAINT `fk_equip_do_grupo_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_equip_do_grupo_grupo`
    FOREIGN KEY (`id_egrupo`)
    REFERENCES `telecom`.`grupos_equip` (`id`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`tipo_acesso`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`tipo_acesso` (
  `id_tipo_acesso` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `protocolo` VARCHAR(45) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id_tipo_acesso`),
  UNIQUE INDEX `protocolo` (`protocolo` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`equiptos_access`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`equiptos_access` (
  `id_equiptos_access` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_equip` INT(10) UNSIGNED NOT NULL,
  `fqdn` VARCHAR(100) NOT NULL,
  `user` VARCHAR(20) NOT NULL,
  `pass` VARCHAR(150) NULL DEFAULT NULL,
  `id_tipo_acesso` INT(10) UNSIGNED NOT NULL,
  `enable_pass` VARCHAR(150) NULL DEFAULT NULL,
  PRIMARY KEY (`id_equiptos_access`),
  UNIQUE INDEX `unique_id_equip_id_tipo_acesso` (`id_equip` ASC, `id_tipo_acesso` ASC),
  INDEX `fk_equiptos_access_equipamentos` (`id_equip` ASC),
  INDEX `fk_equiptos_access_tipo_acesso` (`id_tipo_acesso` ASC),
  CONSTRAINT `fk_equiptos_access_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_equiptos_access_tipo_acesso`
    FOREIGN KEY (`id_tipo_acesso`)
    REFERENCES `telecom`.`tipo_acesso` (`id_tipo_acesso`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `telecom`.`tipo_roteiro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`tipo_roteiro` (
  `id_tipo_roteiro` INT(11) NOT NULL AUTO_INCREMENT,
  `tipo` VARCHAR(40) CHARACTER SET 'latin1' NULL DEFAULT NULL,
  `descricao` VARCHAR(100) CHARACTER SET 'latin1' NULL DEFAULT NULL,
  PRIMARY KEY (`id_tipo_roteiro`),
  UNIQUE INDEX `tipo` (`tipo` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`roteiros`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`roteiros` (
  `id_roteiros` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `roteiro` VARCHAR(40) CHARACTER SET 'latin1' NOT NULL,
  `id_tipo_roteiro` INT(11) NOT NULL,
  `descricao` VARCHAR(100) CHARACTER SET 'latin1' NULL DEFAULT NULL,
  PRIMARY KEY (`id_roteiros`),
  UNIQUE INDEX `roteiros_tipo_unico` (`roteiro` ASC, `id_tipo_roteiro` ASC),
  INDEX `fk_roteiros_tipo_roteiro` (`id_tipo_roteiro` ASC),
  CONSTRAINT `fk_roteiros_tipo_roteiro`
    FOREIGN KEY (`id_tipo_roteiro`)
    REFERENCES `telecom`.`tipo_roteiro` (`id_tipo_roteiro`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`equiptos_roteiros`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`equiptos_roteiros` (
  `id_equiptos_roteiros` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_equip` INT(10) UNSIGNED NOT NULL,
  `id_roteiros` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_equiptos_roteiros`),
  UNIQUE INDEX `uniq_equiptos_roteiros` (`id_equip` ASC, `id_roteiros` ASC),
  INDEX `fk_equiptos_roteiros_equipamentos` (`id_equip` ASC),
  INDEX `fk_equiptos_roteiros_roteiros` (`id_roteiros` ASC),
  CONSTRAINT `fk_equiptos_roteiros_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_equiptos_roteiros_roteiros`
    FOREIGN KEY (`id_roteiros`)
    REFERENCES `telecom`.`roteiros` (`id_roteiros`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`usuarios` (
  `user` VARCHAR(45) CHARACTER SET 'latin1' NOT NULL,
  `pwd` VARCHAR(45) NOT NULL,
  `id_user` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(200) NOT NULL,
  `ativo` TINYINT(4) NOT NULL DEFAULT '1',
  `email` VARCHAR(300) NOT NULL,
  `user_ldap` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id_user`),
  UNIQUE INDEX `key_user` (`user` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`event_log`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`event_log` (
  `id_evento` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_user` INT(10) UNSIGNED NOT NULL,
  `hora_evento` DATETIME NOT NULL,
  `evento` TEXT NOT NULL,
  `resultado` INT(11) NOT NULL,
  `acao` TEXT NULL DEFAULT NULL,
  `funcionalidade` TEXT NULL DEFAULT NULL,
  `parametro_anterior` TEXT NULL DEFAULT NULL,
  `parametro_atual` TEXT NULL DEFAULT NULL,
  `id_objeto` INT(10) NULL DEFAULT NULL,
  PRIMARY KEY (`id_evento`),
  INDEX `fk_event_log_usuarios` (`id_user` ASC),
  CONSTRAINT `fk_event_log_usuarios`
    FOREIGN KEY (`id_user`)
    REFERENCES `telecom`.`usuarios` (`id_user`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'InnoDB free: 0 kB; (`id_user`) REFER `telecom/usuarios`(`id_';


-- -----------------------------------------------------
-- Table `telecom`.`filter_equiptype_xref`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`filter_equiptype_xref` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_filter` INT(10) UNSIGNED NOT NULL,
  `id_equiptype` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_filter_equiptype_xref_filter` (`id_filter` ASC),
  INDEX `fk_filter_equiptype_xref_equiptype` (`id_equiptype` ASC),
  CONSTRAINT `fk_filter_equiptype_xref_equip_type`
    FOREIGN KEY (`id_equiptype`)
    REFERENCES `telecom`.`tipo_equipamento` (`id_tipo_equipamento`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_filter_equiptype_xref_filter`
    FOREIGN KEY (`id_filter`)
    REFERENCES `telecom`.`filter` (`id_filter`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`functionality`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`functionality` (
  `functionality` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`functionality`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`healthcheck`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`healthcheck` (
  `id_healthcheck` INT(11) NOT NULL AUTO_INCREMENT,
  `identifier` VARCHAR(200) NULL DEFAULT NULL,
  `healthcheck_type` VARCHAR(45) NULL DEFAULT NULL,
  `healthcheck_request` VARCHAR(500) NULL DEFAULT NULL,
  `healthcheck_expect` VARCHAR(200) NULL DEFAULT NULL,
  `destination` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id_healthcheck`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`healthcheck_expect`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`healthcheck_expect` (
  `id_healthcheck_expect` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `expect_string` VARCHAR(50) NOT NULL,
  `match_list` VARCHAR(50) NOT NULL,
  `id_ambiente` INT(11) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_healthcheck_expect`, `id_ambiente`),
  INDEX `fk_healthcheck_expect_ambiente` (`id_ambiente` ASC),
  CONSTRAINT `fk_healthcheck_expect_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambiente` (`id_ambiente`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`interfaces`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`interfaces` (
  `id_equip` INT(10) UNSIGNED NOT NULL,
  `interface` VARCHAR(20) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NOT NULL,
  `protegida` TINYINT(1) NOT NULL DEFAULT '1',
  `descricao` VARCHAR(200) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `id_interface` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ligacao_front` INT(10) UNSIGNED NULL DEFAULT NULL,
  `id_ligacao_back` INT(10) UNSIGNED NULL DEFAULT NULL,
  PRIMARY KEY (`id_interface`),
  UNIQUE INDEX `uniq_interface_id_equip` (`interface` ASC, `id_equip` ASC),
  INDEX `fk_interfaces_equipamentos` (`id_equip` ASC),
  INDEX `fk_interfaces_interfaces_front` (`id_ligacao_front` ASC),
  INDEX `fk_interfaces_interfaces_back` (`id_ligacao_back` ASC),
  CONSTRAINT `fk_interfaces_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_interfaces_interfaces_back`
    FOREIGN KEY (`id_ligacao_back`)
    REFERENCES `telecom`.`interfaces` (`id_interface`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_interfaces_interfaces_front`
    FOREIGN KEY (`id_ligacao_front`)
    REFERENCES `telecom`.`interfaces` (`id_interface`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `telecom`.`vlans`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`vlans` (
  `id_vlan` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(50) CHARACTER SET 'latin1' NOT NULL,
  `num_vlan` INT(10) UNSIGNED NOT NULL,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `descricao` VARCHAR(200) CHARACTER SET 'latin1' NULL DEFAULT NULL,
  `acl_file_name` VARCHAR(200) NULL DEFAULT NULL,
  `acl_valida` TINYINT(1) NOT NULL,
  `ativada` TINYINT(4) NOT NULL DEFAULT '0',
  `acl_file_name_v6` VARCHAR(200) NULL DEFAULT NULL,
  `acl_valida_v6` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id_vlan`),
  UNIQUE INDEX `vlan_no_ambiente` (`id_ambiente` ASC, `num_vlan` ASC),
  UNIQUE INDEX `nome_da_vlan_no_ambiente` (`nome` ASC, `id_ambiente` ASC),
  INDEX `fk_vlans_ambiente` (`id_ambiente` ASC),
  CONSTRAINT `fk_vlans_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambiente` (`id_ambiente`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COMMENT = 'Descreve as características da vlan.';


-- -----------------------------------------------------
-- Table `telecom`.`redeipv4`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`redeipv4` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_vlan` INT(10) UNSIGNED NOT NULL,
  `rede_oct1` TINYINT(3) UNSIGNED NOT NULL,
  `rede_oct2` TINYINT(3) UNSIGNED NOT NULL,
  `rede_oct3` TINYINT(3) UNSIGNED NOT NULL,
  `rede_oct4` TINYINT(3) UNSIGNED NOT NULL,
  `bloco` TINYINT(3) UNSIGNED NOT NULL,
  `masc_oct1` TINYINT(3) UNSIGNED NOT NULL,
  `masc_oct2` TINYINT(3) UNSIGNED NOT NULL,
  `masc_oct3` TINYINT(3) UNSIGNED NOT NULL,
  `masc_oct4` TINYINT(3) UNSIGNED NOT NULL,
  `id_tipo_rede` INT(10) UNSIGNED NULL DEFAULT NULL,
  `broadcast` CHAR(15) CHARACTER SET 'latin1' NOT NULL,
  `id_ambientevip` INT(10) UNSIGNED NULL DEFAULT NULL,
  `active` TINYINT(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  INDEX `fk_redeipv4_vlans` (`id_vlan` ASC),
  INDEX `fk_redeipv4_tipo_rede` (`id_tipo_rede` ASC),
  INDEX `fk_redeipv4_ambientevip` (`id_ambientevip` ASC),
  CONSTRAINT `fk_redeipv4_ambientevip`
    FOREIGN KEY (`id_ambientevip`)
    REFERENCES `telecom`.`ambientevip` (`id`),
  CONSTRAINT `fk_redeipv4_tipo_rede`
    FOREIGN KEY (`id_tipo_rede`)
    REFERENCES `telecom`.`tipo_rede` (`id_tipo_rede`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_redeipv4_vlans`
    FOREIGN KEY (`id_vlan`)
    REFERENCES `telecom`.`vlans` (`id_vlan`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`ips`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ips` (
  `id_ip` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `oct4` TINYINT(3) UNSIGNED NOT NULL,
  `oct3` TINYINT(3) UNSIGNED NOT NULL,
  `oct2` TINYINT(3) UNSIGNED NOT NULL,
  `oct1` TINYINT(3) UNSIGNED NOT NULL,
  `descricao` VARCHAR(100) CHARACTER SET 'latin1' NULL DEFAULT NULL,
  `id_redeipv4` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_ip`),
  UNIQUE INDEX `ip_da_rede` (`oct1` ASC, `oct2` ASC, `oct3` ASC, `oct4` ASC, `id_redeipv4` ASC),
  INDEX `fk_ips_redeipv4` (`id_redeipv4` ASC),
  CONSTRAINT `fk_ips_redeipv4`
    FOREIGN KEY (`id_redeipv4`)
    REFERENCES `telecom`.`redeipv4` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`ips_dos_equipamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ips_dos_equipamentos` (
  `id_ips_dos_equipamentos` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ip` INT(10) UNSIGNED NOT NULL,
  `id_equip` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_ips_dos_equipamentos`),
  UNIQUE INDEX `uniq_id_ip_id_equip` (`id_ip` ASC, `id_equip` ASC),
  INDEX `fk_ips_has_equipamentos_ips` (`id_ip` ASC),
  INDEX `fk_ips_has_equipamentos_equipamentos` (`id_equip` ASC),
  CONSTRAINT `fk_ips_has_equipamentos_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_ips_has_equipamentos_ips`
    FOREIGN KEY (`id_ip`)
    REFERENCES `telecom`.`ips` (`id_ip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`redeipv6`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`redeipv6` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ambientevip` INT(10) UNSIGNED NULL DEFAULT NULL,
  `id_vlan` INT(10) UNSIGNED NOT NULL,
  `id_tipo_rede` INT(10) UNSIGNED NULL DEFAULT NULL,
  `bloco1` VARCHAR(4) NOT NULL,
  `bloco2` VARCHAR(4) NOT NULL,
  `bloco3` VARCHAR(4) NOT NULL,
  `bloco4` VARCHAR(4) NOT NULL,
  `bloco5` VARCHAR(4) NOT NULL,
  `bloco6` VARCHAR(4) NOT NULL,
  `bloco7` VARCHAR(4) NOT NULL,
  `bloco8` VARCHAR(4) NOT NULL,
  `bloco` SMALLINT(6) NOT NULL,
  `mask_bloco1` VARCHAR(4) NOT NULL,
  `mask_bloco2` VARCHAR(4) NOT NULL,
  `mask_bloco3` VARCHAR(4) NOT NULL,
  `mask_bloco4` VARCHAR(4) NOT NULL,
  `mask_bloco5` VARCHAR(4) NOT NULL,
  `mask_bloco6` VARCHAR(4) NOT NULL,
  `mask_bloco7` VARCHAR(4) NOT NULL,
  `mask_bloco8` VARCHAR(4) NOT NULL,
  `active` TINYINT(4) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_redeipv6_vlans` (`id_vlan` ASC),
  INDEX `fk_redeipv6_tipo_rede` (`id_tipo_rede` ASC),
  INDEX `fk_redeipv6_ambientevip` (`id_ambientevip` ASC),
  CONSTRAINT `fk_redeipv6_ambientevip`
    FOREIGN KEY (`id_ambientevip`)
    REFERENCES `telecom`.`ambientevip` (`id`),
  CONSTRAINT `fk_redeipv6_tipo_rede`
    FOREIGN KEY (`id_tipo_rede`)
    REFERENCES `telecom`.`tipo_rede` (`id_tipo_rede`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_redeipv6_vlans`
    FOREIGN KEY (`id_vlan`)
    REFERENCES `telecom`.`vlans` (`id_vlan`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`ipsv6`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ipsv6` (
  `id_ipv6` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `descricao` VARCHAR(100) NULL DEFAULT NULL,
  `id_redeipv6` INT(10) UNSIGNED NOT NULL,
  `bloco1` VARCHAR(4) NOT NULL,
  `bloco2` VARCHAR(4) NOT NULL,
  `bloco3` VARCHAR(4) NOT NULL,
  `bloco4` VARCHAR(4) NOT NULL,
  `bloco5` VARCHAR(4) NOT NULL,
  `bloco6` VARCHAR(4) NOT NULL,
  `bloco7` VARCHAR(4) NOT NULL,
  `bloco8` VARCHAR(4) NOT NULL,
  PRIMARY KEY (`id_ipv6`),
  INDEX `fk_ipsv6_redeipv6` (`id_redeipv6` ASC),
  CONSTRAINT `fk_ipsv6_redeipv6`
    FOREIGN KEY (`id_redeipv6`)
    REFERENCES `telecom`.`redeipv6` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`ipsv6_dos_equipamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`ipsv6_dos_equipamentos` (
  `id_ipsv6_dos_equipamentos` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ipv6` INT(10) UNSIGNED NOT NULL,
  `id_equip` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_ipsv6_dos_equipamentos`),
  UNIQUE INDEX `uniq_id_ipv6_id_equip` (`id_ipv6` ASC, `id_equip` ASC),
  INDEX `fk_ipsv6_has_equipamentos_ipsv6` (`id_ipv6` ASC),
  INDEX `fk_ipsv6_has_equipamentos_equipamentos` (`id_equip` ASC),
  CONSTRAINT `fk_ipsv6_has_equipamentos_equipamentos`
    FOREIGN KEY (`id_equip`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`opcoesvip`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`opcoesvip` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `tipo_opcao` CHAR(50) CHARACTER SET 'latin1' NOT NULL,
  `nome_opcao_txt` CHAR(50) CHARACTER SET 'latin1' NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`opcoesvip_ambiente_xref`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`opcoesvip_ambiente_xref` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `id_opcoesvip` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_opcoesvip_ambiente_opcoesvip` (`id_opcoesvip` ASC),
  INDEX `fk_opcoesvip_ambiente_ambiente` (`id_ambiente` ASC),
  CONSTRAINT `fk_opcoesvip_ambiente_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambientevip` (`id`),
  CONSTRAINT `fk_opcoesvip_ambiente_opcoesvip`
    FOREIGN KEY (`id_opcoesvip`)
    REFERENCES `telecom`.`opcoesvip` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`permissions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`permissions` (
  `id_permission` INT(11) NOT NULL AUTO_INCREMENT,
  `function` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_permission`),
  UNIQUE INDEX `function_UNIQUE` (`function` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 29
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`permissoes_administrativas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`permissoes_administrativas` (
  `id_permissoes_administrativas` INT(11) NOT NULL AUTO_INCREMENT,
  `leitura` TINYINT(4) NOT NULL DEFAULT '0',
  `escrita` TINYINT(4) NOT NULL DEFAULT '0',
  `grupos_id` INT(10) UNSIGNED NOT NULL,
  `permission_id` INT(11) NOT NULL,
  PRIMARY KEY (`id_permissoes_administrativas`),
  INDEX `fk_permissoes_administrativas_grupos` (`grupos_id` ASC),
  INDEX `fk_permissoes_administrativas_permissions1_idx` (`permission_id` ASC),
  CONSTRAINT `fk_permissoes_administrativas_grupos`
    FOREIGN KEY (`grupos_id`)
    REFERENCES `telecom`.`grupos` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_permissoes_administrativas_permissions1_idx`
    FOREIGN KEY (`permission_id`)
    REFERENCES `telecom`.`permissions` (`id_permission`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 30
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `telecom`.`rule`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`rule` (
  `id_rule` INT(10) NOT NULL AUTO_INCREMENT,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `name` VARCHAR(80) NOT NULL,
  `id_vip` INT(10) NULL DEFAULT NULL,
  PRIMARY KEY (`id_rule`),
  INDEX `fk_rule_ambiente_idx` (`id_ambiente` ASC),
  INDEX `fk_rule_vip_idx` (`id_vip` ASC),
  CONSTRAINT `fk_rule_vip`
    FOREIGN KEY (`id_vip`)
    REFERENCES `telecom`.`requisicao_vips` (`id_requisicao_vips`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_rule_ambiente`
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `telecom`.`ambiente` (`id_ambiente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`requisicao_vips`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`requisicao_vips` (
  `id_requisicao_vips` INT(11) NOT NULL AUTO_INCREMENT,
  `validado` TINYINT(4) NOT NULL DEFAULT '0',
  `variaveis` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `vip_criado` TINYINT(4) NOT NULL DEFAULT '0',
  `ips_id_ip` INT(10) UNSIGNED NULL DEFAULT NULL,
  `id_healthcheck_expect` INT(10) UNSIGNED NULL DEFAULT NULL,
  `ipsv6_id_ipv6` INT(10) UNSIGNED NULL DEFAULT NULL,
  `l7_filter_to_apply` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `l7_filter_current` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `l7_filter_rollback` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `l7_filter_is_valid` TINYINT(4) NULL DEFAULT NULL,
  `l7_filter_applied_datetime` DATETIME NULL DEFAULT NULL,
  `id_rule` INT(10) NULL DEFAULT NULL,
  `id_rule_current` INT(10) NULL DEFAULT NULL,
  `id_rule_rollback` INT(10) NULL DEFAULT NULL,
  PRIMARY KEY (`id_requisicao_vips`),
  INDEX `fk_requisicao_vips_ips` (`ips_id_ip` ASC),
  INDEX `fk_requisicao_vips_healthcheck_expect` (`id_healthcheck_expect` ASC),
  INDEX `fk_requisicao_vips_ipsv6` (`ipsv6_id_ipv6` ASC),
  INDEX `fk_requisicao_vips_rule_idx` (`id_rule` ASC),
  INDEX `fk_requisicao_vips_rule_current_idx` (`id_rule_current` ASC),
  INDEX `fk_requisicao_vips_rule_rollback_idx` (`id_rule_rollback` ASC),
  CONSTRAINT `fk_requisicao_vips_rule_current`
    FOREIGN KEY (`id_rule_current`)
    REFERENCES `telecom`.`rule` (`id_rule`)
    ON DELETE SET NULL
    ON UPDATE SET NULL,
  CONSTRAINT `fk_requisicao_vips_rule_rollback`
    FOREIGN KEY (`id_rule_rollback`)
    REFERENCES `telecom`.`rule` (`id_rule`)
    ON DELETE SET NULL
    ON UPDATE SET NULL,
  CONSTRAINT `fk_requisicao_vips_healthcheck_expect`
    FOREIGN KEY (`id_healthcheck_expect`)
    REFERENCES `telecom`.`healthcheck_expect` (`id_healthcheck_expect`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_requisicao_vips_ips`
    FOREIGN KEY (`ips_id_ip`)
    REFERENCES `telecom`.`ips` (`id_ip`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_requisicao_vips_ipsv6`
    FOREIGN KEY (`ipsv6_id_ipv6`)
    REFERENCES `telecom`.`ipsv6` (`id_ipv6`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_requisicao_vips_rule`
    FOREIGN KEY (`id_rule`)
    REFERENCES `telecom`.`rule` (`id_rule`)
    ON DELETE SET NULL
    ON UPDATE SET NULL)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `telecom`.`rule_content`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`rule_content` (
  `id_rule_content` INT(10) NOT NULL AUTO_INCREMENT,
  `content` TEXT NOT NULL,
  `order` INT(10) NOT NULL,
  `id_rule` INT(10) NOT NULL,
  PRIMARY KEY (`id_rule_content`),
  INDEX `fk_rule_content_idx` (`id_rule` ASC),
  CONSTRAINT `fk_rule_content`
    FOREIGN KEY (`id_rule`)
    REFERENCES `telecom`.`rule` (`id_rule`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`semaforo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`semaforo` (
  `id_semaforo` INT(5) UNSIGNED NOT NULL,
  `descricao` VARCHAR(50) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NOT NULL,
  PRIMARY KEY (`id_semaforo`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `telecom`.`server_pool`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`server_pool` (
  `id_server_pool` INT(11) NOT NULL AUTO_INCREMENT,
  `identifier` VARCHAR(200) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `healthcheck_id_healthcheck` INT(11) NULL DEFAULT NULL,
  `default_port` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_server_pool`),
  INDEX `fk_server_pool_healthcheck1_idx` (`healthcheck_id_healthcheck` ASC),
  CONSTRAINT `fk_server_pool_healthcheck1`
    FOREIGN KEY (`healthcheck_id_healthcheck`)
    REFERENCES `telecom`.`healthcheck` (`id_healthcheck`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `telecom`.`server_pool_member`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`server_pool_member` (
  `id_server_pool_member` INT(11) NOT NULL AUTO_INCREMENT,
  `id_server_pool` INT(11) NOT NULL,
  `identifier` VARCHAR(200) NULL DEFAULT NULL,
  `ipsv6_id_ipv6` INT(10) UNSIGNED NULL DEFAULT NULL,
  `ips_id_ip` INT(10) UNSIGNED NULL DEFAULT NULL,
  `priority` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `weight` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `limit` INT(11) NOT NULL DEFAULT '0',
  `port` INT(10) UNSIGNED NOT NULL,
  `healthcheck_id_healthcheck` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id_server_pool_member`),
  UNIQUE INDEX `unique_pool_member` (`id_server_pool` ASC, `ips_id_ip` ASC, `port` ASC),
  UNIQUE INDEX `unique_pool_member_ipv6` (`id_server_pool` ASC, `ipsv6_id_ipv6` ASC, `port` ASC),
  INDEX `fk_server_pool_ipsv61_idx` (`ipsv6_id_ipv6` ASC),
  INDEX `fk_server_pool_ips1_idx` (`ips_id_ip` ASC),
  INDEX `fk_server_pool_member_server_pool1_idx` (`id_server_pool` ASC),
  INDEX `fk_server_pool_member_healthcheck1_idx` (`healthcheck_id_healthcheck` ASC),
  CONSTRAINT `fk_server_pool_ips1`
    FOREIGN KEY (`ips_id_ip`)
    REFERENCES `telecom`.`ips` (`id_ip`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_server_pool_ipsv61`
    FOREIGN KEY (`ipsv6_id_ipv6`)
    REFERENCES `telecom`.`ipsv6` (`id_ipv6`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_server_pool_member_healthcheck1`
    FOREIGN KEY (`healthcheck_id_healthcheck`)
    REFERENCES `telecom`.`healthcheck` (`id_healthcheck`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_server_pool_member_server_pool1`
    FOREIGN KEY (`id_server_pool`)
    REFERENCES `telecom`.`server_pool` (`id_server_pool`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`usuarios_do_grupo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`usuarios_do_grupo` (
  `id_usuarios_do_grupo` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_user` INT(10) UNSIGNED NOT NULL,
  `id_grupo` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_usuarios_do_grupo`),
  UNIQUE INDEX `uniq_id_user_id_grupo` (`id_user` ASC, `id_grupo` ASC),
  INDEX `fk_users_do_grupo_users` (`id_user` ASC),
  INDEX `fk_users_do_grupo_grupos` (`id_grupo` ASC),
  CONSTRAINT `fk_users_do_grupo_grupos`
    FOREIGN KEY (`id_grupo`)
    REFERENCES `telecom`.`grupos` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_do_grupo_users`
    FOREIGN KEY (`id_user`)
    REFERENCES `telecom`.`usuarios` (`id_user`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`vip_port_to_pool`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`vip_port_to_pool` (
  `id_vip_port_to_pool` INT(11) NOT NULL AUTO_INCREMENT,
  `id_requisicao_vips` INT(11) NOT NULL,
  `id_server_pool` INT(11) NOT NULL,
  `vip_port` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`id_vip_port_to_pool`),
  INDEX `fk_vip_port_to_pool_requisicao_vips1_idx` (`id_requisicao_vips` ASC),
  INDEX `fk_vip_port_to_pool_server_pool1_idx` (`id_server_pool` ASC),
  CONSTRAINT `fk_vip_port_to_pool_requisicao_vips1`
    FOREIGN KEY (`id_requisicao_vips`)
    REFERENCES `telecom`.`requisicao_vips` (`id_requisicao_vips`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_vip_port_to_pool_server_pool1`
    FOREIGN KEY (`id_server_pool`)
    REFERENCES `telecom`.`server_pool` (`id_server_pool`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `telecom`.`racks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telecom`.`racks` (
  `id_rack` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `numero` INT(10) UNSIGNED NOT NULL,
  `mac_sw1` VARCHAR(17) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `mac_sw2` VARCHAR(17) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `mac_ilo` VARCHAR(17) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL,
  `id_equip1` INT(10) UNSIGNED NULL DEFAULT NULL,
  `id_equip2` INT(10) UNSIGNED NULL DEFAULT NULL,
  `id_equip3` INT(10) UNSIGNED NULL DEFAULT NULL,
  INDEX `fk_racks_id_equip1` (`id_equip1` ASC),
  INDEX `fk_racks_id_equip2` (`id_equip2` ASC),
  INDEX `fk_racks_id_equip3` (`id_equip3` ASC),
  PRIMARY KEY (`id_rack`),
  CONSTRAINT `fk_racks_id_equip1`
    FOREIGN KEY (`id_equip1`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_racks_id_equip2`
    FOREIGN KEY (`id_equip2`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON UPDATE CASCADE,
  CONSTRAINT `fk_racks_id_equip3`
    FOREIGN KEY (`id_equip3`)
    REFERENCES `telecom`.`equipamentos` (`id_equip`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


LOCK TABLES `grupos` WRITE;
INSERT INTO `grupos` VALUES (1,'Administrators','S','S','S','S'),(2,'Guests','S','N','N','N');
UNLOCK TABLES;

LOCK TABLES `permissions` WRITE;
INSERT INTO `permissions` VALUES (1,'administracao_usuarios'),(2,'administrativa'),(3,'alocar_vlan'),(4,'ambiente_vip'),(5,'authenticate'),(6,'cadastro_de_ambiente'),(7,'cadastro_de_equipamentos'),(8,'cadastro_de_grupos_equipamentos'),(9,'cadastro_de_marca'),(10,'cadastro_de_roteiro'),(11,'cadastro_de_tipo_acesso'),(12,'cadastro_de_tipo_rede'),(13,'cadastro_de_vlans'),(14,'cadastro_de_vm'),(15,'healthcheck_expect'),(16,'ips'),(17,'opcao_vip'),(18,'requisicao_vips'),(19,'script_alterar_vip'),(20,'script_alterar_vlan'),(21,'script_criacao_vip'),(22,'script_criacao_vlan'),(23,'validar_acl_vlans'),(24,'validar_vip'),(25,'administracao_vips'),(26,'audit_logs'),(27,'script_remover_vip'),(28,'aplicar_acl');
UNLOCK TABLES;

LOCK TABLES `permissoes_administrativas` WRITE;
INSERT INTO `permissoes_administrativas` VALUES (1,1,1,1,1),(2,1,1,1,2),(3,1,1,1,3),(4,1,1,1,4),(5,1,1,1,5),(6,1,1,1,6),(7,1,1,1,7),(8,1,1,1,8),(9,1,1,1,9),(10,1,1,1,10),(11,1,1,1,11),(12,1,1,1,12),(13,1,1,1,13),(14,1,1,1,14),(15,1,1,1,15),(16,1,1,1,16),(17,1,1,1,17),(18,1,1,1,18),(19,1,1,1,19),(20,1,1,1,20),(21,1,1,1,21),(22,1,1,1,22),(23,1,1,1,23),(24,1,1,1,24),(25,1,1,1,25),(26,1,1,1,26),(27,1,1,1,27),(28,1,1,1,28),(29,0,1,2,5);
UNLOCK TABLES;

LOCK TABLES `usuarios_do_grupo` WRITE;
INSERT INTO `usuarios_do_grupo` VALUES (1,1,1);
UNLOCK TABLES;

LOCK TABLES `usuarios` WRITE;
INSERT INTO `usuarios` VALUES ('ADMIN','c21f969b5f03d33d43e04f8f136e7682',1,'Administrator',1,'admin@networkapi',NULL);
UNLOCK TABLES;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

