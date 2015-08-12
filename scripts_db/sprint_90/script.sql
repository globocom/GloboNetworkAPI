ALTER TABLE `vlans` ADD COLUMN `acl_draft` TEXT NULL  AFTER `acl_valida_v6` , ADD COLUMN `acl_draft_v6` VARCHAR(45) NULL  AFTER `acl_draft` ;
