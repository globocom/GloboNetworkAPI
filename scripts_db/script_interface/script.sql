ALTER TABLE `interfaces` ADD COLUMN `vlans` VARCHAR(200) ;


ALTER TABLE `telecom`.`interfaces` ADD COLUMN `id_tipo_interface` INT UNSIGNED NOT NULL DEFAULT 1 AFTER `id_ligacao_back` , 
  ADD CONSTRAINT `fk_interfaces_tipo_interface`
  FOREIGN KEY (`id_tipo_interface` )
  REFERENCES `telecom`.`tipo_interface` (`id_tipo_interface` )
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
  , ADD INDEX `fk_interfaces_tipo_interface_idx` (`id_tipo_interface` ASC) ;
