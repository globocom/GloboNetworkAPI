CREATE TABLE IF NOT EXISTS `port_channel` (
  `id_port_channel` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(10) NOT NULL UNIQUE,
  `lacp` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_port_channel`),
  UNIQUE INDEX `nome_unique` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `interfaces` ADD `id_channel` INT(10) UNSIGNED DEFAULT NULL after id_tipo_interface;

ALTER TABLE interfaces ADD INDEX `fk_interfaces_port_channel` (`id_channel` ASC),
 ADD CONSTRAINT `fk_interfaces_port_channel`
    FOREIGN KEY (`id_channel`)
    REFERENCES `telecom`.`port_channel` (`id_port_channel`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


