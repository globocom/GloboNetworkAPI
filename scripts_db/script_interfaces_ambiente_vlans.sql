CREATE TABLE IF NOT EXISTS `tipo_interface` (
  `id_tipo_interface` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `tipo` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_tipo_interface`),
  UNIQUE INDEX `tipo_unique` (`tipo` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;

INSERT into tipo_interface (id_tipo_interface, tipo) values (1, "access");
INSERT into tipo_interface (id_tipo_interface, tipo) values (2, "trunk");

ALTER TABLE `interfaces`
 ADD `vlan_nativa` VARCHAR(200) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT 1 AFTER `id_ligacao_back`,
 ADD `id_tipo_interface` INT(10) UNSIGNED NOT NULL DEFAULT 1 after vlan_nativa;

ALTER TABLE interfaces ADD INDEX `fk_interfaces_interfaces_tipo` (`id_tipo_interface` ASC),
 ADD CONSTRAINT `fk_interfaces_interfaces_tipo`
    FOREIGN KEY (`id_tipo_interface`)
    REFERENCES `tipo_interface` (`id_tipo_interface`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT


CREATE TABLE IF NOT EXISTS `interface_do_ambiente` (
  `id_int_ambiente` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_ambiente` INT(10) UNSIGNED NOT NULL,
  `id_interface` INT(10) UNSIGNED NOT NULL,
  `vlans` VARCHAR(200) CHARACTER SET `utf8` COLLATE `utf8_unicode_ci` DEFAULT NULL,
  PRIMARY KEY (`id_int_ambiente`),
  UNIQUE INDEX `interface_do_ambiente_unique` (`id_ambiente` ASC, `id_interface` ASC),
  INDEX `fk_interface_do_ambiente_ambiente` (`id_ambiente` ASC),
  INDEX `fk_interface_do_ambiente_interface` (`id_interface` ASC),
  CONSTRAINT `interface_do_ambiente_ambiente `
    FOREIGN KEY (`id_ambiente`)
    REFERENCES `ambiente` (`id_ambiente`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `interface_do_ambiente_interface `
    FOREIGN KEY (`id_interface`)
    REFERENCES `interfaces` (`id_interface`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;

