-- load_example_environment.sql
--
-- Script for load into your database the environment used for documentation examples
--
-- Host: localhost    Database: networkapi
--
-- Current Database: `networkapi`
--
-- ----------------------------------------------------------------------------------
-- Dumping data for table `config`

SET @id_as_management_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'as_management');
SET @id_neighbor_management_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'neighbor_management');
SET @id_virtual_interface_management_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'virtual_interface_management');
SET @id_neighbor_create_script_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'neighbor_create_script');
SET @id_neighbor_remove_script_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'neighbor_remove_script');

SET @id_list_config_bgp_management_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'list_config_bgp_management');
SET @id_peer_group_management_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'peer_group_management');
SET @id_route_map_management_perm := (SELECT `id_permission` FROM `permissions` WHERE function = 'route_map_management');

INSERT INTO
   `config` (id_config, ip_v4_min, ip_v4_max, ip_v6_min, ip_v6_max)
VALUES
   (
      1, 2, 3, 0, 0
   )
;
-- Dumping data for table `object_type`
INSERT INTO
   `object_type` (`name`)
VALUES
   (
      'ServerPool'
   )
,
   (
      'VipRequest'
   )
,
   (
      'Vlan'
   )
;

SET @id_pool_obj_name := (SELECT `id` FROM `object_type` WHERE name = 'ServerPool');
SET @id_vip_obj_name := (SELECT `id` FROM `object_type` WHERE name = 'VipRequest');
SET @id_vlan_obj_name := (SELECT `id` FROM `object_type` WHERE name = 'Vlan');
SET @id_peer_obj_name := (SELECT `id` FROM `object_type` WHERE name = 'PeerGroup');

-- Dumping data for table `marcas`
INSERT INTO
   `marcas`
VALUES
   (
      1, 'MARCA'
   )
;
-- Dumping data for table `modelos`
INSERT INTO
   `modelos`
VALUES
   (
      1, 'MODELO', 1
   )
;
-- Dumping data for table `tipo_equipamento`
INSERT INTO
   `tipo_equipamento`
VALUES
   (
      1, 'Switch'
   )
,
   (
      2, 'Servidor'
   )
,
   (
      3, 'Roteador'
   )
,
   (
      5, 'Balanceador'
   )
;
-- Dumping data for table `filter`
INSERT INTO
   `filter`
VALUES
   (
      1, 'Servidores', 'Servidores'
   )
;
-- Dumping data for table `filter_equiptype_xref`
INSERT INTO
   `filter_equiptype_xref` (`id`, `id_filter`, `id_equiptype`)
VALUES
   (
      '1', '1', '2'
   )
;

-- Dumping data for table `ambiente_logico`
BEGIN;

INSERT INTO
   `ambiente_logico`
VALUES
   (
      11, 'AMBIENTE_LOGICO_RED'
   )
,
   (
      12, 'AMBIENTE_LOGICO_BLUE'
   )
,
   (
      13, 'AMBIENTE_LOGICO_GREEN'
   )
,
   (
      14, 'AMBIENTE_LOGICO_YELLOW'
   )
,
   (
      15, 'AMBIENTE_LOGICO_ORANGE'
   )
,
   (
      16, 'AMBIENTE_LOGICO_POOL'
   )
,
   (
      17, 'AMBIENTE_LOGICO_SPACE_1'
   )
,
   (
      18, 'AMBIENTE_LOGICO_SPACE_2'
   )
;
-- Dumping data for table `divisao_dc`
INSERT INTO
   `divisao_dc`
VALUES
   (
      21, 'DIVISAO_DC_RED'
   )
,
   (
      22, 'DIVISAO_DC_BLUE'
   )
,
   (
      23, 'DIVISAO_DC_GREEN'
   )
,
   (
      24, 'DIVISAO_DC_YELLOW'
   )
,
   (
      25, 'DIVISAO_DC_ORANGE'
   )
,
   (
      26, 'DIVISAO_DC_POOL'
   )
,
   (
      27, 'DIVISAO_DC_SPACE_1'
   )
,
   (
      28, 'DIVISAO_DC_SPACE_2'
   )
;
-- Dumping data for table `grupo_l3`
INSERT INTO
   `grupo_l3`
VALUES
   (
      31, 'GRUPO_L3_RED'
   )
,
   (
      32, 'GRUPO_L3_BLUE'
   )
,
   (
      33, 'GRUPO_L3_GREEN'
   )
,
   (
      34, 'GRUPO_L3_YELLOW'
   )
,
   (
      35, 'GRUPO_L3_ORANGE'
   )
,
   (
      36, 'GRUPO_L3_POOL'
   )
,
   (
      37, 'GRUPO_L3_SPACE_1'
   )
,
   (
      38, 'GRUPO_L3_SPACE_2'
   )
;

-- Dumping data for table `vrf`
INSERT INTO
   `vrf` (id, internal_name, vrf)
VALUES
   (
      1, 'default', 'default'
   )
,
   (
      2, 'Vrf-1', 'Vrf-1'
   )
,
   (
      3, 'Vrf-2', 'Vrf-2'
   )
;
-- Dumping data for table `ambiente`
INSERT INTO
   `ambiente` (`id_ambiente`, `id_grupo_l3`, `id_ambiente_logic`, `id_divisao`, `link`, `acl_path`, `id_filter`, `min_num_vlan_1`, `max_num_vlan_1`, `min_num_vlan_2`, `max_num_vlan_2`, `id_father_environment`, `id_vrf`)
VALUES
   (
      1, 31, 11, 21, ' http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'Red', '1', '11', '20', '0', '0', NULL, 1
   )
,
   (
      2, 32, 12, 22, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'Blue', '1', '21', '30', '0', '0', NULL, 1
   )
,
   (
      3, 33, 13, 23, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'Green', '1', '31', '31', '0', '0', NULL, 1
   )
,
   (
      4, 34, 14, 24, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'Yellow', '1', '20', '20', '0', '0', NULL, 1
   )
,
   (
      5, 35, 15, 25, ' http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'Orange', '1', '15', '19', '0', '0', NULL, 1
   )
,
   (
      6, 35, 11, 21, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'Other Color', '1', '1', '500', '501', '1000', NULL, 1
   )
,
   (
      7, 32, 13, 21, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '15', '19', '0', '0', NULL, 1
   )
,
   (
      8, 33, 14, 21, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '15', '19', '0', '0', NULL, 1
   )
,
   (
      9, 33, 11, 21, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '1', '500', '501', '1000', NULL, 1
   )
,
   (
      10, 33, 12, 21, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '1', '500', '501', '1000', NULL, 1
   )
,
   (
      11, 36, 16, 26, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '1', '500', '501', '1000', NULL, 1
   )
,
   (
      12, 37, 17, 27, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '1', '500', '501', '1000', NULL, 1
   )
,
   (
      13, 38, 18, 28, 'http://globonetworkapi.readthedocs.org/en/latest/definitions.html#environment', 'NULL', '1', '1', '500', '501', '1000', NULL, 1
   )
;

-- Dumping data for table `ambientevip`
INSERT INTO
   `ambientevip`
VALUES
   (
      1, 'Red', 'Red', 'Red', 'Red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      2, 'Red', 'Blue', 'red', 'red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      3, 'Red', 'Green', 'Red', 'Red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      4, 'Red', 'Yellow', 'Red', 'Red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      5, 'Red', 'Orange', 'Red', 'Red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      6, 'Blue', 'Red', 'Red', 'Red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      7, 'Blue', 'Blue', 'Red', 'Red', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      8, 'Blue', 'Blue', 'Blue', 'Blue', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      9, 'Green', 'Green', 'Green', 'Green', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      10, 'Yellow', 'Yellow', 'Yellow', 'Yellow', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      11, 'Orange', 'Orange', 'Orange', 'Orange', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      12, 'EnvironmentVIP NetworkAPI Test', 'Test', 'Test', 'Test', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      13, 'Fin-Test', 'ClientTxt-Test', 'EnvP44Txt-Test', 'Description-Test', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
,
   (
      14, 'FIN_VIP', 'ClientTxt-VIP', 'EnvP44Txt-VIP', 'Description-VIP', '{"conf":{"keys":[],"layers":[],"optionsvip_extended":{}}}'
   )
;
-- Dumping data for table `environment_environment_vip`
INSERT INTO
   `environment_environment_vip` (id, environment_id, environment_vip_id)
VALUES
   (
      1, 9, 13
   )
,
   (
      2, 12, 14
   )
,
   (
      3, 13, 14
   )
;
-- Dumping data for table `opcoesvip`
INSERT INTO
   `opcoesvip` (id, tipo_opcao, nome_opcao_txt)
VALUES
   (
      1, 'Balanceamento', 'least-conn'
   )
,
   (
      2, 'Balanceamento', 'round-robin'
   )
,
   (
      3, 'Balanceamento', 'weighted'
   )
,
   (
      4, 'Balanceamento', 'uri hash'
   )
,
   (
      5, 'Persistencia', '(nenhum)'
   )
,
   (
      6, 'Persistencia', 'source-ip'
   )
,
   (
      7, 'Persistencia', 'source-ip com persist. entre portas'
   )
,
   (
      8, 'Persistencia', 'cookie'
   )
,
   (
      9, 'Retorno de trafego', 'Normal'
   )
,
   (
      10, 'Retorno de trafego', 'DSRL3'
   )
,
   (
      11, 'timeout', '5'
   )
,
   (
      12, 'timeout', '10'
   )
,
   (
      13, 'cache', '(nenhum)'
   )
,
   (
      14, 'cache', 'cache1'
   )
,
   (
      15, 'cache', 'cache2'
   )
,
   (
      16, 'cache', 'cache3'
   )
,
   (
      17, 'l7_protocol', 'HTTP'
   )
,
   (
      18, 'l7_protocol', 'FTP'
   )
,
   (
      19, 'l7_protocol', 'Outros'
   )
,
   (
      20, 'l4_protocol', 'TCP'
   )
,
   (
      21, 'l4_protocol', 'UDP'
   )
,
   (
      22, 'l7_protocol', 'HTTPS'
   )
,
   (
      23, 'l7_rule', 'default_vip'
   )
,
   (
      24, 'l7_rule', 'default_glob'
   )
,
   (
      25, 'l7_rule', 'glob'
   )
;
-- Dumping data for table `opcoesvip_ambiente_xref`
INSERT INTO
   `opcoesvip_ambiente_xref` (`id`, `id_ambiente`, `id_opcoesvip`)
VALUES
   (
      '1', '14', '1'
   )
,
   (
      '2', '14', '2'
   )
,
   (
      '3', '14', '3'
   )
,
   (
      '4', '14', '4'
   )
,
   (
      '5', '14', '5'
   )
,
   (
      '6', '14', '6'
   )
,
   (
      '7', '14', '7'
   )
,
   (
      '8', '14', '8'
   )
,
   (
      '9', '14', '9'
   )
,
   (
      '10', '14', '10'
   )
,
   (
      '11', '14', '11'
   )
,
   (
      '12', '14', '12'
   )
,
   (
      '13', '14', '13'
   )
,
   (
      '14', '14', '14'
   )
,
   (
      '15', '14', '15'
   )
,
   (
      '16', '14', '16'
   )
,
   (
      '17', '14', '17'
   )
,
   (
      '18', '14', '18'
   )
,
   (
      '19', '14', '19'
   )
,
   (
      '20', '14', '20'
   )
,
   (
      '21', '14', '21'
   )
,
   (
      '22', '14', '22'
   )
,
   (
      '23', '14', '23'
   )
,
   (
      '24', '14', '24'
   )
,
   (
      '25', '14', '25'
   )
,
   (
      '26', '13', '1'
   )
,
   (
      '27', '13', '5'
   )
;
-- Dumping data for table `tipo_rede`
INSERT INTO
   `tipo_rede`
VALUES
   (
      2, 'Ponto a ponto'
   )
,
   (
      6, 'Rede invalida equipamentos'
   )
,
   (
      7, 'Rede invalida NAT'
   )
,
   (
      8, 'Rede invalida VIP'
   )
,
   (
      9, 'Rede valida equipamentos'
   )
,
   (
      10, 'Rede valida NAT'
   )
,
   (
      11, 'Rede valida VIP'
   )
;
-- Dumping data for table `ip_config`
INSERT INTO
   `ip_config` (id_ip_config, subnet, new_prefix, type, network_type)
VALUES
   (
      1, '172.16.0.5/24', '24', 'v4', 2
   )
,
   (
      2, '10.0.0.5/24', '24', 'v4', 2
   )
,
   (
      3, '192.168.0.0/30', '30', 'v4', 2
   )
,
   (
      4, '192.168.1.0/30', '30', 'v4', 2
   )
,
   (
      5, '10.0.1.0/28', '28', 'v4', 2
   )
,
   (
      10, '10.42.0.0/24', '24', 'v4', 2
   )
,
   (
      11, '192.168.104.0/22', '27', 'v4', 2
   )
,
   (
      12, 'fdbe:bebe:bebe:11c0:0000:0000:0000:0000/58', '64', 'v6', 2
   )
,
   (
      13, '10.237.128.0/18', '28', 'v4', 2
   )
,
   (
      14, 'fdbe:bebe:bebe:1200:0:0:0:0/57', '64', 'v6', 2
   )
,
   (
      15, '10.16.0.0/16', '24', 'v4', 2
   )
,
   (
      16, '10.0.0.0/16', '24', 'v4', 2
   )
,
   (
      17, '10.1.0.0/16', '24', 'v4', 2
   )
;
-- Dumping data for table `ip_config`
INSERT INTO
   `config_do_ambiente` (id_config_do_ambiente, id_ambiente, id_ip_config)
VALUES
   (
      7, 1, 5
   )
,
   (
      8, 1, 10
   )
,
   (
      11, 9, 11
   )
,
   (
      12, 9, 12
   )
,
   (
      13, 10, 13
   )
,
   (
      14, 10, 14
   )
,
   (
      15, 11, 15
   )
,
   (
      16, 12, 16
   )
,
   (
      17, 13, 17
   )
;
-- Dumping data for table `environment_cidr`
INSERT INTO
   `environment_cidr` (id, network, subnet_mask, ip_version, id_network_type, id_env, network_first_ip, network_last_ip, network_mask)
VALUES
   (
      5, '10.0.1.0/28', '28', 'v4', 2, 1, 167772416, 167772431, 28
   )
,
   (
      10, '10.42.0.0/24', '24', 'v4', 2, 1, 170524672, 170524927, 24
   )
,
   (
      11, '192.168.104.0/22', '27', 'v4', 2, 9, 3232262144, 3232263167, 22
   )
,
   (
      12, 'fdbe:bebe:bebe:11c0:0000:0000:0000:0000/58', '64', 'v6', 2, 9, 337285088106912836215476086841679020032, 337285088106912837396067707559090323455, 58
   )
,
   (
      13, '10.237.128.0/18', '28', 'v4', 2, 10, 183336960, 183353343, 18
   )
,
   (
      14, 'fdbe:bebe:bebe:1200:0:0:0:0/57', '64', 'v6', 2, 10, 337285088106912837396067707559090323456, 337285088106912839757250948993912930303, 57
   )
,
   (
      15, '10.16.0.0/16', '24', 'v4', 2, 11, 168820736, 168886271, 16
   )
,
   (
      16, '10.0.0.0/16', '24', 'v4', 2, 12, 167772160, 167837695, 16
   )
,
   (
      17, '10.1.0.0/16', '24', 'v4', 2, 13, 167837696, 167903231, 16
   )
;
-- Dumping data for table `vlans`
INSERT INTO
   `vlans` (id_vlan, nome, num_vlan, id_ambiente, descricao, acl_file_name, acl_valida, ativada, acl_file_name_v6, acl_valida_v6, acl_draft, acl_draft_v6, vrf)
VALUES
   (
      1, 'Vlan 31', 31, 3, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      2, 'Vlan 20', 20, 4, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      3, 'Vlan 11', 11, 1, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      4, 'Vlan 21', 21, 2, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      5, 'Vlan 22', 22, 2, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      6, 'Vlan 21', 21, 5, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      7, 'Vlan 15', 15, 5, '', '', 1, 1, NULL, 0, 1, NULL, NULL
   )
,
   (
      9, 'Vlan-Test-Eqpt', 1, 9, NULL, NULL, 0, 0, NULL, 0, NULL, NULL, NULL
   )
,
   (
      10, 'Vlan-Test-Pool', 1, 10, NULL, NULL, 0, 0, NULL, 0, NULL, NULL, NULL
   )
,
   (
      11, 'Vlan Pool', 1, 11, NULL, NULL, 0, 0, NULL, 0, NULL, NULL, NULL
   )
,
   (
      12, 'Vlan Space 1', 1, 12, NULL, NULL, 0, 0, NULL, 0, NULL, NULL, NULL
   )
,
   (
      13, 'Vlan Space 2', 1, 13, NULL, NULL, 0, 0, NULL, 0, NULL, NULL, NULL
   )
;
-- Dumping data for table `equipamentos`
INSERT INTO
   `equipamentos` (id_equip, id_tipo_equipamento, id_modelo, nome, maintenance)
VALUES
   (
      1, 1, 1, 'SWITCH-R1', 0
   )
,
   (
      2, 1, 1, 'SWITCH-R2', 0
   )
,
   (
      3, 1, 1, 'SWITCH-R3', 0
   )
,
   (
      4, 1, 1, 'SWITCH-B1', 0
   )
,
   (
      5, 1, 1, 'SWITCH-B2', 0
   )
,
   (
      6, 1, 1, 'SWITCH-B3', 0
   )
,
   (
      7, 1, 1, 'SWITCH-01', 0
   )
,
   (
      8, 1, 1, 'SWITCH-02', 0
   )
,
   (
      9, 1, 1, 'SWITCH-03', 0
   )
,
   (
      10, 3, 1, 'SR1', 0
   )
,
   (
      11, 3, 1, 'SR2', 0
   )
,
   (
      12, 3, 1, 'ROUTER', 0
   )
,
   (
      13, 2, 1, 'SERVER-S1', 0
   )
,
   (
      14, 2, 1, 'SERVER-P1', 0
   )
,
   (
      15, 2, 1, 'SERVER-P2', 0
   )
,
   (
      16, 2, 1, 'SERVER-P3', 0
   )
,
   (
      17, 2, 1, 'SERVER-P4', 0
   )
,
   (
      18, 2, 1, 'SERVER-P5', 0
   )
,
   (
      19, 5, 1, 'LOAD-BALANCER', 0
   )
,
   (
      20, 2, 1, 'SERVER-SPACE-1', 0
   )
,
   (
      21, 2, 1, 'SERVER-SPACE-2', 0
   )
,
   (
      22, 1, 1, 'TOR-1-SPACE-1', 0
   )
,
   (
      23, 1, 1, 'TOR-2-SPACE-1', 0
   )
,
   (
      24, 1, 1, 'TOR-1-SPACE-2', 0
   )
,
   (
      25, 1, 1, 'TOR-2-SPACE-2', 0
   )
,
   (
      26, 3, 1, 'FABRIC-ROUTER-0', 0
   )
,
   (
      27, 3, 1, 'FABRIC-ROUTER-1', 0
   )
;

-- Dumping data for table `tipo_acesso`
INSERT INTO
    `tipo_acesso` (`id_tipo_acesso`, `protocolo`)
VALUES
    (
        1, 'http'
    )
,
    (
        2, 'https'
    )
,
    (
        3, 'ssh'
    )
,
    (
        4, 'telnet'
    )
;

-- Dumping data for table `equip_do_ambiente`
INSERT INTO
   `equip_do_ambiente` (id_equip_do_ambiente, id_ambiente, id_equip, is_router, is_controller)
VALUES
   (
      1, 9, 14, 0, 0
   )
,
   (
      2, 9, 15, 0, 0
   )
,
   (
      3, 9, 16, 0, 0
   )
,
   (
      4, 9, 17, 0, 0
   )
,
   (
      5, 9, 18, 0, 0
   )
,
   (
      6, 10, 19, 0, 0
   )
,
   (
      7, 12, 20, 0, 0
   )
,
   (
      8, 13, 21, 0, 0
   )
,
   (
      9, 12, 22, 0, 0
   )
,
   (
      10, 12, 23, 0, 0
   )
,
   (
      11, 13, 24, 0, 0
   )
,
   (
      12, 13, 25, 0, 0
   )
,
   (
      13, 11, 19, 0, 0
   )
,
   (
      14, 10, 12, 1, 0
   )
,
   (
      15, 1, 26, 1, 0
   )
,
   (
      16, 1, 27, 1, 0
   )
;

-- Dumping data for table `redeipv4`
INSERT INTO
   `redeipv4` (id, id_vlan, rede_oct1, rede_oct2, rede_oct3, rede_oct4, bloco, masc_oct1, masc_oct2, masc_oct3, masc_oct4, id_tipo_rede, broadcast, id_ambientevip, active, cluster_unit)
VALUES
   (
      1, 1, 192, 168, 0, 0, 30, 255, 255, 255, 0, 2, '192.168.0.3', NULL, 0, NULL
   )
,
   (
      2, 2, 192, 168, 1, 0, 30, 255, 255, 255, 0, 2, '192.168.1.3', NULL, 0, NULL
   )
,
   (
      3, 4, 172, 16, 0, 5, 24, 255, 255, 255, 0, 2, '172.16.0.255', NULL, 0, NULL
   )
,
   (
      4, 7, 10, 0, 0, 5, 30, 255, 255, 255, 0, 2, '10.0.0.255', NULL, 0, NULL
   )
,
   (
      7, 3, 10, 42, 0, 0, 24, 255, 255, 255, 0, 2, '10.42.0.255', NULL, 1, NULL
   )
,
   (
      5, 9, 192, 168, 104, 0, 27, 255, 255, 255, 224, 2, '192.168.104.31', NULL, 0, NULL
   )
,
   (
      6, 10, 10, 237, 128, 0, 28, 255, 255, 255, 240, 2, '10.237.128.15', 13, 0, NULL
   )
,
   (
      8, 11, 10, 16, 0, 0, 24, 255, 255, 255, 0, 8, '10.16.0.255', 14, 1, NULL
   )
,
   (
      9, 12, 10, 0, 0, 0, 24, 255, 255, 255, 0, 2, '10.0.0.255', NULL, 1, NULL
   )
,
   (
      10, 13, 10, 1, 0, 0, 24, 255, 255, 255, 0, 2, '10.1.0.255', NULL, 1, NULL
   )
;
-- Dumping data for table `ips`
INSERT INTO
   `ips` (id_ip, oct4, oct3, oct2, oct1, descricao, id_redeipv4)
VALUES
   (
      1, 1, 0, 168, 192, 'SR1', 1
   )
,
   (
      2, 2, 0, 168, 192, 'ROUTER', 1
   )
,
   (
      3, 1, 1, 168, 192, 'ROUTER', 2
   )
,
   (
      4, 2, 1, 168, 192, 'SR2', 2
   )
,
   (
      5, 6, 0, 16, 172, 'SERVER-S1', 3
   )
,
   (
      6, 6, 0, 0, 10, 'SERVER-S1', 4
   )
,
   (
      7, 2, 104, 168, 192, 'IPv4 of Real P1', 5
   )
,
   (
      8, 3, 104, 168, 192, 'IPv4 of Real P2', 5
   )
,
   (
      9, 4, 104, 168, 192, 'IPv4 of Real P3', 5
   )
,
   (
      10, 5, 104, 168, 192, 'IPv4 of Real P4', 5
   )
,
   (
      11, 6, 104, 168, 192, 'IPv4 of Real P5', 5
   )
,
   (
      12, 1, 0, 0, 10, 'IPv4(gateway) of TORs Space 1', 9
   )
,
   (
      13, 1, 0, 1, 10, 'IPv4(gateway) of TORs Space 2', 10
   )
,
   (
      14, 254, 0, 0, 10, 'IPv4 of TOR 1 Space 1', 9
   )
,
   (
      15, 253, 0, 0, 10, 'IPv4 of TOR 2 Space 1', 9
   )
,
   (
      16, 254, 0, 1, 10, 'IPv4 of TOR 1 Space 2', 10
   )
,
   (
      17, 253, 0, 1, 10, 'IPv4 of TOR 2 Space 2', 10
   )
,
   (
      18, 2, 0, 0, 10, 'IPv4 of Real Server Space 1', 9
   )
,
   (
      19, 2, 0, 1, 10, 'IPv4 of Real Server Space 2', 10
   )
,
   (
      20, 2, 0, 16, 10, 'IP of VIP 1', 8
   )
;
-- Dumping data for table `ips_dos_equipamentos`
INSERT INTO
   `ips_dos_equipamentos` (id_ips_dos_equipamentos, id_ip, id_equip)
VALUES
   (
      1, 1, 10
   )
,
   (
      2, 2, 12
   )
,
   (
      3, 3, 12
   )
,
   (
      4, 4, 11
   )
,
   (
      5, 5, 13
   )
,
   (
      6, 6, 13
   )
,
   (
      7, 7, 14
   )
,
   (
      8, 8, 15
   )
,
   (
      9, 9, 16
   )
,
   (
      10, 10, 17
   )
,
   (
      11, 11, 18
   )
,
   (
      12, 12, 22
   )
,
   (
      13, 12, 23
   )
,
   (
      14, 14, 22
   )
,
   (
      15, 15, 23
   )
,
   (
      16, 13, 24
   )
,
   (
      17, 13, 25
   )
,
   (
      18, 16, 24
   )
,
   (
      19, 17, 25
   )
,
   (
      20, 18, 20
   )
,
   (
      21, 19, 21
   )
,
   (
      22, 20, 19
   )
;
-- Dumping data for table 'redeipv6'
INSERT INTO
   `redeipv6` (id, id_ambientevip, id_vlan, id_tipo_rede, bloco1, bloco2, bloco3, bloco4, bloco5, bloco6, bloco7, bloco8, bloco, mask_bloco1, mask_bloco2, mask_bloco3, mask_bloco4, mask_bloco5, mask_bloco6, mask_bloco7, mask_bloco8, active, cluster_unit)
VALUES
   (
      1, NULL, 9, 2, 'fdbe', 'bebe', 'bebe', '11c0', '0000', '0000', '0000', '0000', 64, 'ffff', 'ffff', 'ffff', 'ffff', '0000', '0000', '0000', '0000', 0, NULL
   )
,
   (
      2, 13, 10 , 2, 'fdbe', 'bebe', 'bebe', '1200', '0000', '0000', '0000', '0000', 64, 'ffff', 'ffff', 'ffff', 'ffff', '0000', '0000', '0000', '0000', 0, NULL
   )
;
-- Dumping data for table `ipsv6`
INSERT INTO
   `ipsv6` (id_ipv6, descricao, id_redeipv6, bloco1, bloco2, bloco3, bloco4, bloco5, bloco6, bloco7, bloco8)
VALUES
   (
      1, 'IPv6 of Real P1', 1, 'fdbe', 'bebe', 'bebe', '11c0', '0000', '0000', '0000', '0001'
   )
,
   (
      2, 'IPv6 of Real P2', 1, 'fdbe', 'bebe', 'bebe', '11c0', '0000', '0000', '0000', '0002'
   )
,
   (
      3, 'IPv6 of Real P3', 1, 'fdbe', 'bebe', 'bebe', '11c0', '0000', '0000', '0000', '0003'
   )
,
   (
      4, 'IPv6 of Real P4', 1, 'fdbe', 'bebe', 'bebe', '11c0', '0000', '0000', '0000', '0004'
   )
,
   (
      5, 'IPv6 of Real P5', 1, 'fdbe', 'bebe', 'bebe', '11c0', '0000', '0000', '0000', '0005'
   )
;
-- Dumping data for table `ipsv6_dos_equipamentos`
INSERT INTO
   `ipsv6_dos_equipamentos` (id_ipsv6_dos_equipamentos, id_ipv6, id_equip)
VALUES
   (
      1, 1, 14
   )
,
   (
      2, 2, 15
   )
,
   (
      3, 3, 16
   )
,
   (
      4, 4, 17
   )
,
   (
      5, 5, 18
   )
;
-- Dumping data for table `usuarios`
INSERT INTO
   `usuarios` (USER, pwd, id_user, nome, ativo, email, user_ldap)
VALUES
   (
      'networkapi', MD5('networkapi'), 1, 'Globo Network API test user', 1, 'networkapi@globo.com', NULL
   )
,
   (
      'testeapi', MD5('testeapi'), 114, 'Test user to be used by the development database', 1, 'testeapi@globo.com', NULL
   )
,
   (
      'cadvlan', MD5('12345678'), 2, 'Cadvlan - user of authentication', 1, 'suptel@corp.globo.com', NULL
   )
;
-- Dumping data for table `grupos`
INSERT INTO
   `grupos` (id, nome, leitura, escrita, edicao, exclusao)
VALUES
   (
      1, 'Admin', 'S', 'S', 'S', 'S'
   )
,
   (
      2, 'Cadvlan_adm', 'N', 'N', 'N', 'N'
   )
;
-- Dumping data for table `usuarios_do_grupo`
INSERT INTO
   `usuarios_do_grupo` (id_usuarios_do_grupo, id_user, id_grupo)
VALUES
   (
      1, 1, 1
   )
,
   (
      3, 114, 1
   )
,
   (
      2, 2, 2
   )
;
-- Dumping data for table `permissions`
INSERT INTO
   `permissions` (`id_permission`, `function`)
VALUES
   (
      1, 'administracao_usuarios'
   )
,
   (
      2, 'administrativa'
   )
,
   (
      3, 'alocar_vlan'
   )
,
   (
      4, 'ambiente_vip'
   )
,
   (
      5, 'authenticate'
   )
,
   (
      6, 'cadastro_de_ambiente'
   )
,
   (
      7, 'cadastro_de_equipamentos'
   )
,
   (
      8, 'cadastro_de_grupos_equipamentos'
   )
,
   (
      9, 'cadastro_de_marca'
   )
,
   (
      10, 'cadastro_de_roteiro'
   )
,
   (
      11, 'cadastro_de_tipo_acesso'
   )
,
   (
      12, 'cadastro_de_tipo_rede'
   )
,
   (
      13, 'cadastro_de_vlans'
   )
,
   (
      14, 'cadastro_de_vm'
   )
,
   (
      15, 'healthcheck_expect'
   )
,
   (
      16, 'ips'
   )
,
   (
      17, 'opcao_vip'
   )
,
   (
      18, 'requisicao_vips'
   )
,
   (
      19, 'script_alterar_vip'
   )
,
   (
      20, 'script_alterar_vlan'
   )
,
   (
      21, 'script_criacao_vip'
   )
,
   (
      22, 'script_criacao_vlan'
   )
,
   (
      23, 'validar_acl_vlans'
   )
,
   (
      24, 'validar_vip'
   )
,
   (
      25, 'administracao_vips'
   )
,
   (
      26, 'audit_logs'
   )
,
   (
      27, 'script_remover_vip'
   )
,
   (
      28, 'aplicar_acl'
   )
,
   (
      29, 'cadastro_de_pool'
   )
,
   (
      30, 'script_remover_pool'
   )
,
   (
      31, 'script_criacao_pool'
   )
,
   (
      32, 'script_alterar_pool'
   )
;
-- Dumping data for table `permissoes_administrativas`
INSERT INTO
   `permissoes_administrativas` (id_permissoes_administrativas, leitura, escrita, grupos_id, permission_id)
VALUES
   (
      1, 1, 1, 1, 1
   )
,
   (
      2, 1, 1, 1, 2
   )
,
   (
      3, 1, 1, 1, 3
   )
,
   (
      4, 1, 1, 1, 4
   )
,
   (
      5, 1, 1, 1, 5
   )
,
   (
      6, 1, 1, 1, 6
   )
,
   (
      7, 1, 1, 1, 7
   )
,
   (
      8, 1, 1, 1, 8
   )
,
   (
      9, 1, 1, 1, 9
   )
,
   (
      10, 1, 1, 1, 10
   )
,
   (
      11, 1, 1, 1, 11
   )
,
   (
      12, 1, 1, 1, 12
   )
,
   (
      13, 1, 1, 1, 13
   )
,
   (
      14, 1, 1, 1, 14
   )
,
   (
      15, 1, 1, 1, 15
   )
,
   (
      16, 1, 1, 1, 16
   )
,
   (
      17, 1, 1, 1, 17
   )
,
   (
      18, 1, 1, 1, 18
   )
,
   (
      19, 1, 1, 1, 19
   )
,
   (
      20, 1, 1, 1, 20
   )
,
   (
      21, 1, 1, 1, 21
   )
,
   (
      22, 1, 1, 1, 22
   )
,
   (
      23, 1, 1, 1, 23
   )
,
   (
      24, 1, 1, 1, 24
   )
,
   (
      25, 1, 1, 1, 25
   )
,
   (
      26, 1, 1, 1, 26
   )
,
   (
      27, 1, 1, 1, 27
   )
,
   (
      28, 1, 1, 1, 28
   )
,
   (
      29, 1, 1, 1, 29
   )
,
   (
      30, 1, 1, 1, 30
   )
,
   (
      31, 1, 1, 1, 31
   )
,
   (
      32, 1, 1, 1, 32
   )
,
   (
      33, 1, 1, 2, 1
   )
,
   (
      34, 1, 1, 2, 5
   )
,
   (
      35, 1, 1, 1, @id_as_management_perm
   )
,
   (
      36, 1, 1, 2, @id_as_management_perm
   )
,
   (
      37, 1, 1, 1, @id_neighbor_management_perm
   )
,
   (
      38, 1, 1, 2, @id_neighbor_management_perm
   )
,
   (
      39, 1, 1, 1, @id_virtual_interface_management_perm
   )
,
   (
      40, 1, 1, 2, @id_virtual_interface_management_perm
   )
,
   (
      41, 1, 1, 1, @id_neighbor_create_script_perm
   )
,
   (
      42, 1, 1, 2, @id_neighbor_create_script_perm
   )
,
   (
      43, 1, 1, 1, @id_neighbor_remove_script_perm
   )
,
   (
      44, 1, 1, 2, @id_neighbor_remove_script_perm
   )
,
   (
      45, 1, 1, 1, @id_list_config_bgp_management_perm
   )
,
   (
      46, 1, 1, 2, @id_list_config_bgp_management_perm
   )
,
   (
      47, 1, 1, 1, @id_peer_group_management_perm
   )
,
   (
      48, 1, 1, 2, @id_peer_group_management_perm
   )
,
   (
      49, 1, 1, 1, @id_route_map_management_perm
   )
,
   (
      50, 1, 1, 2, @id_route_map_management_perm
   )
;

-- Dumping data for table `grupos_equip`
INSERT INTO
   `grupos_equip` (id, nome)
VALUES
   (
      1, 'Grupo de Equipamento Teste Network API'
   )
;
-- Dumping data for table `equip_do_grupo`
INSERT INTO
   `equip_do_grupo` (id_equip_do_grupo, id_egrupo, id_equip)
VALUES
   (
      1, 1, 1
   )
,
   (
      2, 1, 2
   )
,
   (
      3, 1, 3
   )
,
   (
      4, 1, 4
   )
,
   (
      5, 1, 5
   )
,
   (
      6, 1, 6
   )
,
   (
      7, 1, 7
   )
,
   (
      8, 1, 8
   )
,
   (
      9, 1, 9
   )
,
   (
      10, 1, 10
   )
,
   (
      11, 1, 11
   )
,
   (
      12, 1, 12
   )
,
   (
      13, 1, 13
   )
,
   (
      14, 1, 14
   )
,
   (
      15, 1, 15
   )
,
   (
      16, 1, 16
   )
,
   (
      17, 1, 17
   )
,
   (
      18, 1, 18
   )
,
   (
      19, 1, 19
   )
;
-- Dumping data for table `direitos_grupoequip`
INSERT INTO
   `direitos_grupoequip` (id_direito, id_ugrupo, id_egrupo, leitura, escrita, alterar_config, exclusao)
VALUES
   (
      1, 1, 1, 1, 1, 1, 1
   )
;
-- Dumping data for table `optionspool`
INSERT INTO
   `optionspool` (id_optionspool, type, description)
VALUES
   (
      1, 'HealthCheck', 'TCP'
   )
,
   (
      2, 'HealthCheck', 'HTTP'
   )
,
   (
      3, 'HealthCheck', 'UDP'
   )
,
   (
      4, 'HealthCheck', 'HTTPS'
   )
,
   (
      5, 'ServiceDownAction', 'none'
   )
,
   (
      6, 'ServiceDownAction', 'drop'
   )
,
   (
      7, 'ServiceDownAction', 'reset'
   )
,
   (
      8, 'ServiceDownAction', 'reselect'
   )
;
-- Dumping data for table `healthcheck`
INSERT INTO
   `healthcheck` (`id_healthcheck`, `identifier`, `healthcheck_type`, `healthcheck_request`, `healthcheck_expect`, `destination`)
VALUES
   (
      1, '', 'TCP', '', '', '*:*'
   )
;
-- Dumping data for table `server_pool`
INSERT INTO
   `server_pool` (id_server_pool, identifier, healthcheck_id_healthcheck, `service-down-action_id`, default_port, default_limit, ambiente_id_ambiente, pool_criado, lb_method)
VALUES
   (
      1, 'Pool_1', 1, 5, 8080, 100, 11, 1, 'least-conn'
   )
;
-- Dumping data for table `server_pool_member`
INSERT INTO
   `server_pool_member` (`id_server_pool_member`, `id_server_pool`, `identifier`, `ips_id_ip`, `priority`, `weight`, `LIMIT`, `port`, `status`)
VALUES
   (
      1, 1, '10.0.0.2', 18, 0, 1, 1000, 8080, 7
   )
,
   (
      2, 1, '10.1.0.2', 19, 0, 1, 1000, 8080, 7
   )
;
-- Dumping data for table `vip_request`
INSERT INTO
   `vip_request` (`id`, `id_environmentvip`, `id_ipv4`, `name`, `service`, `business`, `created`)
VALUES
   (1, 14, 20, 'vip_teste', 'vip_teste', 'vip_teste', '0');

-- Dumping data for table `vip_request_dscp`
INSERT INTO
   `vip_request_dscp` (`id`, `id_vip_request`, `dscp`)
VALUES
   (1, 1, 3);
-- Dumping data for table `vip_request_optionsvip`
INSERT INTO
   `vip_request_optionsvip` (`id`, `id_vip_request`, `id_opcoesvip`)
VALUES
   (1, 1, 13)
,
   (2, 1, 10)
,
   (3, 1, 11)
,
   (4, 1, 7)
;
-- Dumping data for table `vip_request_port`
INSERT INTO
   `vip_request_port` (`id`, `id_vip_request`, `port`)
VALUES
   (1, 1, '8080');
-- Dumping data for table `vip_request_port_optionsvip`
INSERT INTO
   `vip_request_port_optionsvip` (`id`, `id_vip_request_port`, `id_opcoesvip`)
VALUES
   (1, 1, 20)
,
   (2, 1, 17)
;
-- Dumping data for table `vip_request_port_pool`
INSERT INTO
   `vip_request_port_pool` (`id`, `id_vip_request_port`, `id_opcoesvip`, `id_server_pool`)
VALUES
   (1, 1, 23, 1);

-- Dumping data for table `object_group_permission`
INSERT INTO
   `object_group_permission` (`id_user_group`, `id_object_type`, `id_object`, `read`, `write`, `change_config`, `delete`)
VALUES
   (
      1, 1, 1, '1', '1', '1', '1'
   )
,
   (
      1, 2, 1, '1', '1', '1', '1'
   )
;

INSERT INTO
   `object_group_permission_general` (`id`, `id_user_group`, `id_object_type`, `read`, `write`, `change_config`, `delete`)
VALUES
   (
      1, 1, @id_pool_obj_name, '1', '1', '1', '1'
   )
,
   (
      2, 1, @id_vip_obj_name, '1', '1', '1', '1'
   )
,
   (
      3, 1, @id_vlan_obj_name, '1', '1', '1', '1'
   )
,
   (
      4, 1, @id_peer_obj_name, '1', '1', '1', '1'
   )
;


--
-- Dumped data of the Interface types table
--
INSERT INTO `tipo_interface` (`tipo`)
VALUES ("access"), ("trunk");




--
-- Global commit!
--
COMMIT;
