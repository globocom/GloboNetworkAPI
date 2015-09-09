ALTER TABLE `telecom`.`equipamentos` 
ADD COLUMN `maintenance` TINYINT NULL;

ALTER TABLE `telecom`.`server_pool` 
ADD COLUMN `service-down-action_id` INT(11) NULL;

ALTER TABLE `telecom`.`server_pool`
ADD INDEX (`service-down-action_id` ASC);

CREATE TABLE `telecom`.`optionspool` (
  `id_optionspool` INT NOT NULL,
  `type` VARCHAR(50) NOT NULL,
  `description` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_optionspool`));

ALTER TABLE `telecom`.`server_pool` 
ADD CONSTRAINT `fk_server_pool_optionpool`
  FOREIGN KEY (`service-down-action_id`)
  REFERENCES `telecom`.`optionspool` (`id_optionspool`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


