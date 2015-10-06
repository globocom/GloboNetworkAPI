ALTER TABLE `requisicao_vips` ADD COLUMN `id_traffic_return` INT(11) DEFAULT 12;
INSERT INTO opcoesvip (tipo_opcao,nome_opcao_txt) values ('Retorno de trafego', 'DSRL3');

CREATE TABLE `dsrl3id_requisicao_vips_xref` (
  `id_dsrl3id_to_vip_xref` int(11) NOT NULL AUTO_INCREMENT,
  `id_dsrl3` int(11) NOT NULL,
  `id_requisicao_vips` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id_dsrl3id_to_vip_xref`),
  KEY `fk_dsrl3id_to_vip_idx` (`id_requisicao_vips`),
  CONSTRAINT `fk_dsrl3id_to_vip1` FOREIGN KEY (`id_requisicao_vips`) REFERENCES `requisicao_vips` (`id_requisicao_vips`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=16733 DEFAULT CHARSET=utf8;
