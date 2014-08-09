# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''


class AdminPermission(object):
    USER_ADMINISTRATION = 'administracao_usuarios'
    ENVIRONMENT_MANAGEMENT = 'cadastro_de_ambiente'
    NETWORK_TYPE_MANAGEMENT = 'cadastro_de_tipo_rede'
    SCRIPT_MANAGEMENT = 'cadastro_de_roteiro'
    BRAND_MANAGEMENT = 'cadastro_de_marca'
    ACCESS_TYPE_MANAGEMENT = 'cadastro_de_tipo_acesso'
    EQUIPMENT_MANAGEMENT = 'cadastro_de_equipamentos'
    EQUIPMENT_GROUP_MANAGEMENT = 'cadastro_de_grupos_equipamentos'
    VM_MANAGEMENT = 'cadastro_de_vm'
    VLAN_MANAGEMENT = 'cadastro_de_vlans'
    VLAN_CREATE_SCRIPT = 'script_criacao_vlan'
    VLAN_ALTER_SCRIPT = 'script_alterar_vlan'
    VLAN_ALLOCATION = 'alocar_vlan'
    TELCO_CONFIGURATION = 'configuracao_telco'
    HEALTH_CHECK_EXPECT = 'healthcheck_expect'
    IPS = 'ips'
    VIPS_REQUEST = 'requisicao_vips'
    VIP_ALTER_SCRIPT = 'script_alterar_vip'
    VIP_CREATE_SCRIPT = 'script_criacao_vip'
    VIP_REMOVE_SCRIPT = 'script_remover_vip'
    VIP_VALIDATION = 'validar_vip'
    ACL_VLAN_VALIDATION = 'validar_acl_vlans'
    ENVIRONMENT_VIP = 'ambiente_vip'
    OPTION_VIP = 'opcao_vip'
    AUTHENTICATE = 'authenticate'
    AUDIT_LOG = 'audit_logs'
    ACL_APPLY = 'aplicar_acl'

    EQUIP_READ_OPERATION = 'READ'
    EQUIP_WRITE_OPERATION = 'WRITE'
    EQUIP_UPDATE_CONFIG_OPERATION = 'UPDATE_CONFIG'
    READ_OPERATION = 'READ'
    WRITE_OPERATION = 'WRITE'
