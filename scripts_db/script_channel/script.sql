CREATE TABLE IF NOT EXISTS `port_channel` (
  `id_port_channel` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `lacp` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_port_channel`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `interfaces` ADD `id_channel` INT(10) UNSIGNED DEFAULT NULL after id_tipo_interface;

ALTER TABLE interfaces ADD INDEX `fk_interfaces_port_channel` (`id_channel` ASC),
 ADD CONSTRAINT `fk_interfaces_port_channel`
    FOREIGN KEY (`id_channel`)
    REFERENCES `port_channel` (`id_port_channel`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
