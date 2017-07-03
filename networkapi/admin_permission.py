# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
    POOL_MANAGEMENT = 'cadastro_de_pool'
    POOL_CREATE_SCRIPT = 'script_criacao_pool'
    POOL_REMOVE_SCRIPT = 'script_remover_pool'
    POOL_ALTER_SCRIPT = 'script_alterar_pool'
    NETWORK_FORCE = 'network_force'

    EQUIP_READ_OPERATION = 'READ'
    EQUIP_WRITE_OPERATION = 'WRITE'
    EQUIP_UPDATE_CONFIG_OPERATION = 'UPDATE_CONFIG'
    READ_OPERATION = 'READ'
    WRITE_OPERATION = 'WRITE'

    POOL_READ_OPERATION = 'READ'
    POOL_WRITE_OPERATION = 'WRITE'
    POOL_DELETE_OPERATION = 'DELETE'
    POOL_UPDATE_CONFIG_OPERATION = 'UPDATE_CONFIG'

    VIP_READ_OPERATION = 'READ'
    VIP_WRITE_OPERATION = 'WRITE'
    VIP_DELETE_OPERATION = 'DELETE'
    VIP_UPDATE_CONFIG_OPERATION = 'UPDATE_CONFIG'

    OBJ_READ_OPERATION = 'READ'
    OBJ_WRITE_OPERATION = 'WRITE'
    OBJ_DELETE_OPERATION = 'DELETE'
    OBJ_UPDATE_CONFIG_OPERATION = 'UPDATE_CONFIG'

    OBJ_TYPE_VLAN = 'Vlan'
    OBJ_TYPE_POOL = 'ServerPool'
    OBJ_TYPE_VIP = 'VipRequest'

