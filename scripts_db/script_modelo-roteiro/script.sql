CREATE TABLE IF NOT EXISTS `modelo_roteiro` (
  `id_modelo_roteiro` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_roteiro` int(10) unsigned NOT NULL,
  `id_modelo` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id_modelo_roteiro`),
  INDEX `fk_modelo_roteiro_id_roteiro` (`id_roteiro` ASC),
  INDEX `fk_modelo_roteiro_id_modelo` (`id_modelo` ASC),
  CONSTRAINT `modelo_roteiro_id_roteiro` FOREIGN KEY (`id_roteiro`) REFERENCES `roteiros` (`id_roteiros`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `modelo_roteiro_id_modelo` FOREIGN KEY (`id_modelo`) REFERENCES `modelos` (`id_modelo`) ON DELETE NO ACTION ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8;


