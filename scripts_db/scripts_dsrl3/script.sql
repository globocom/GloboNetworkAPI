ALTER TABLE `requisicao_vips` ADD COLUMN `id_traffic_return` INT(11) DEFAULT 12;
INSERT INTO opcoesvip (tipo_opcao,nome_opcao_txt) values ('Retorno de trafego', 'DSRL3');

CREATE TABLE `dsrl3_to_vip` (
  `id_dsrl3_to_vip` int(11) NOT NULL AUTO_INCREMENT,
  `id_dsrl3` int(11) NOT NULL,
  `id_requisicao_vips` int(11) NOT NULL,
  PRIMARY KEY (`id_dsrl3_to_vip`),
  KEY `fk_dsrl3_to_vip` (`id_requisicao_vips`),
  CONSTRAINT `fk_dsrl3_to_vip1` FOREIGN KEY (`id_requisicao_vips`) REFERENCES `requisicao_vips` (`id_requisicao_vips`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;


update  opcoesvip set nome_opcao_txt= 'DSRL2' where id = 13;

#essa linha poe os mesmos ambientes para o dsrl3 que o "normal" tem
insert into opcoesvip_ambiente_xref (id_ambiente, id_opcoesvip) SELECT distinct id_ambiente, 48 from opcoesvip_ambiente_xref where id_opcoesvip=12;
