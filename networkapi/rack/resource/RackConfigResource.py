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
import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from netaddr import IPNetwork
from requests.exceptions import RequestException

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.rack.models import Rack
from networkapi.rack.models import RackConfigError
from networkapi.rack.models import RackError
from networkapi.rack.models import RackNumberNotFoundError
from networkapi.rack.resource.GeraConfig import autoprovision_coreoob
from networkapi.rack.resource.GeraConfig import autoprovision_splf
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.system import exceptions as var_exceptions
from networkapi.system.facade import get_value as get_variable

log = logging.getLogger(__name__)

if int(get_variable('use_foreman')):
    from foreman.client import Foreman, ForemanException


def buscar_roteiro(id_sw, tipo):

    roteiros = EquipamentoRoteiro.search(None, id_sw)
    for rot in roteiros:
        if (rot.roteiro.tipo_roteiro.tipo == tipo):
            roteiro_eq = rot.roteiro.roteiro
    roteiro_eq = roteiro_eq.lower()
    if '.txt' not in roteiro_eq:
        roteiro_eq = roteiro_eq + '.txt'

    return roteiro_eq


def buscar_ip(id_sw):
    """Retuns switch IP that is registered in a management environment
    """

    ip_sw = None

    ips = IpEquipamento()
    ips_equip = ips.list_by_equip(id_sw)
    regexp = re.compile(r'GERENCIA')

    mgnt_ip = None
    for ip_equip in ips_equip:
        ip_sw = ip_equip.ip
        if ip_sw is not None:
            if regexp.search(ip_sw.networkipv4.vlan.ambiente.ambiente_logico.nome) is not None:
                mgnt_ip = str(ip_sw.oct1) + '.' + str(ip_sw.oct2) + \
                    '.' + str(ip_sw.oct3) + '.' + str(ip_sw.oct4)

    return mgnt_ip


def gera_config(rack):

    id_core1 = None
    id_core2 = None
    name_sp1 = None
    name_sp2 = None
    name_sp3 = None
    name_sp4 = None
    name_core1 = None
    name_core2 = None
    int_sp1 = None
    int_sp2 = None
    int_sp3 = None
    int_sp4 = None
    int_lf1_sp1 = None
    int_lf1_sp2 = None
    int_lf2_sp3 = None
    int_lf2_sp4 = None
    int_oob_mgmtlf1 = None
    int_oob_mgmtlf2 = None
    int_oob_core1 = None
    int_oob_core2 = None
    int_core1_oob = None
    int_core2_oob = None
    prefix_spine = 'SPN'
    prefix_oob = 'OOB'

    # Equipamentos
    num_rack = rack.numero
    try:
        id_lf1 = rack.id_sw1.id
        name_lf1 = rack.id_sw1.nome
        id_lf2 = rack.id_sw2.id
        name_lf2 = rack.id_sw2.nome
        id_oob = rack.id_ilo.id
        name_oob = rack.id_ilo.nome
    except:
        raise RackConfigError(None, rack.nome, 'Erro: Rack incompleto.')

    # Interface leaf01
    try:
        interfaces = Interface.search(id_lf1)
        for interface in interfaces:
            try:
                sw = interface.get_switch_and_router_interface_from_host_interface(
                    None)
                if sw.equipamento.nome.split('-')[0] == prefix_spine:
                    if sw.equipamento.nome.split('-')[2] == '01' or sw.equipamento.nome.split('-')[2] == '1':
                        int_lf1_sp1 = interface.interface
                        name_sp1 = sw.equipamento.nome
                        id_sp1 = sw.equipamento.id
                        int_sp1 = sw.interface
                    elif sw.equipamento.nome.split('-')[2] == '02' or sw.equipamento.nome.split('-')[2] == '2':
                        int_lf1_sp2 = interface.interface
                        name_sp2 = sw.equipamento.nome
                        id_sp2 = sw.equipamento.id
                        int_sp2 = sw.interface
                elif sw.equipamento.nome.split('-')[0] == prefix_oob:
                    int_oob_mgmtlf1 = sw.interface
            except:
                pass
    except InterfaceNotFoundError:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar as interfaces associadas ao Leaf 01.')

    if int_sp1 is None or int_sp2 is None or int_oob_mgmtlf1 is None:
        raise RackConfigError(
            None, rack.nome, 'Erro: As interfaces do Leaf01 nao foram cadastradas.')

    # Interface leaf02
    try:
        interfaces1 = Interface.search(id_lf2)
        for interface1 in interfaces1:
            try:
                sw = interface1.get_switch_and_router_interface_from_host_interface(
                    None)
                if sw.equipamento.nome.split('-')[0] == prefix_spine:
                    if sw.equipamento.nome.split('-')[2] == '03' or sw.equipamento.nome.split('-')[2] == '3':
                        int_lf2_sp3 = interface1.interface
                        name_sp3 = sw.equipamento.nome
                        id_sp3 = sw.equipamento.id
                        int_sp3 = sw.interface
                    elif sw.equipamento.nome.split('-')[2] == '04' or sw.equipamento.nome.split('-')[2] == '4':
                        int_lf2_sp4 = interface1.interface
                        name_sp4 = sw.equipamento.nome
                        id_sp4 = sw.equipamento.id
                        int_sp4 = sw.interface
                elif sw.equipamento.nome.split('-')[0] == prefix_oob:
                    int_oob_mgmtlf2 = sw.interface
            except:
                pass
    except InterfaceNotFoundError:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar as interfaces associadas ao Leaf 02.')

    if int_sp3 is None or int_sp4 is None or int_oob_mgmtlf2 is None:
        raise RackConfigError(
            None, rack.nome, 'Erro: As interfaces do Leaf02 nao foram cadastradas.')

    # Interface OOB
    try:
        interfaces2 = Interface.search(id_oob)
        for interface2 in interfaces2:
            try:
                sw = interface2.get_switch_and_router_interface_from_host_interface(
                    None)
                if sw.equipamento.nome.split('-')[0] == prefix_oob:
                    if sw.equipamento.nome.split('-')[2] == '01' or sw.equipamento.nome.split('-')[2] == '1':
                        int_oob_core1 = interface2.interface
                        name_core1 = sw.equipamento.nome
                        int_core1_oob = sw.interface
                        id_core1 = sw.equipamento.id
                    elif sw.equipamento.nome.split('-')[2] == '02' or sw.equipamento.nome.split('-')[2] == '2':
                        int_oob_core2 = interface2.interface
                        name_core2 = sw.equipamento.nome
                        int_core2_oob = sw.interface
                        id_core2 = sw.equipamento.id
            except:
                pass
    except InterfaceNotFoundError:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar as interfaces associadas ao Switch de gerencia.')

    if int_oob_core1 is None or int_core1_oob is None or int_oob_core2 is None or int_core2_oob is None:
        raise RackConfigError(
            None, rack.nome, 'Erro: As interfaces do Switch de gerencia nao foram cadastradas.')

    # Roteiro LF01
    try:
        FILEINLF1 = buscar_roteiro(id_lf1, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Leaf 01.')

    # Roteiro LF02
    try:
        FILEINLF2 = buscar_roteiro(id_lf2, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Leaf 02.')

    # Roteiro SPN01
    try:
        FILEINSP1 = buscar_roteiro(id_sp1, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Spine 01.')

    # Roteiro SPN02
    try:
        FILEINSP2 = buscar_roteiro(id_sp2, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Spine 02.')

    # Roteiro SPN03
    try:
        FILEINSP3 = buscar_roteiro(id_sp3, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Spine 03.')

    # Roteiro SPN04
    try:
        FILEINSP4 = buscar_roteiro(id_sp4, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Spine 04.')

    # Roteiro Core 01
    try:
        FILEINCR1 = buscar_roteiro(id_core1, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Core 01.')

    # Roteiro Core 02
    try:
        FILEINCR2 = buscar_roteiro(id_core2, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do Core 02.')

    # Roteiro OOB
    try:
        FILEINOOB = buscar_roteiro(id_oob, 'CONFIGURACAO')
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o roteiro do switch de gerencia.')

    # Ip LF01
    try:
        ip_mgmtlf1 = buscar_ip(id_lf1)
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o ip de gerencia do leaf 01.')

    # Ip LF02
    try:
        ip_mgmtlf2 = buscar_ip(id_lf2)
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o ip de gerencia do leaf 02.')

    # Ip OOB
    try:
        ip_mgmtoob = buscar_ip(id_oob)
    except:
        raise RackConfigError(
            None, rack.nome, 'Erro ao buscar o ip de gerencia do oob.')

    try:
        NETWORKAPI_USE_FOREMAN = int(get_variable('use_foreman'))
        NETWORKAPI_FOREMAN_URL = get_variable('foreman_url')
        NETWORKAPI_FOREMAN_USERNAME = get_variable('foreman_username')
        NETWORKAPI_FOREMAN_PASSWORD = get_variable('foreman_password')
        FOREMAN_HOSTS_ENVIRONMENT_ID = get_variable(
            'foreman_hosts_environment_id')
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando as variáveis relativas ao Foreman.')

    # begin - Create Foreman entries for rack switches
    if NETWORKAPI_USE_FOREMAN:
        foreman = Foreman(NETWORKAPI_FOREMAN_URL, (NETWORKAPI_FOREMAN_USERNAME,
                                                   NETWORKAPI_FOREMAN_PASSWORD), api_version=2)

        # for each switch, check the switch ip against foreman know networks, finds foreman hostgroup
        # based on model and brand and inserts the host in foreman
        # if host already exists, delete and recreate with new information
        for [switch, mac] in [[rack.id_sw1, rack.mac_sw1], [rack.id_sw2, rack.mac_sw2], [rack.id_ilo, rack.mac_ilo]]:
            # Get all foremand subnets and compare with the IP address of the
            # switches until find it
            if mac is None:
                raise RackConfigError(
                    None, rack.nome, ('Could not create entry for %s. There is no mac address.' % (switch.nome)))

            ip = buscar_ip(switch.id)
            if ip is None:
                raise RackConfigError(
                    None, rack.nome, ('Could not create entry for %s. There is no management IP.' % (switch.nome)))

            switch_cadastrado = 0
            for subnet in foreman.subnets.index()['results']:
                network = IPNetwork(ip + '/' + subnet['mask']).network
                # check if switches ip network is the same as
                # subnet['subnet']['network'] e subnet['subnet']['mask']
                if network.__str__() == subnet['network']:
                    subnet_id = subnet['id']
                    hosts = foreman.hosts.index(search=switch.nome)['results']
                    if len(hosts) == 1:
                        foreman.hosts.destroy(id=hosts[0]['id'])
                    elif len(hosts) > 1:
                        raise RackConfigError(
                            None, rack.nome, ('Could not create entry for %s. There are multiple entries with the sam name.' % (switch.nome)))

                    # Lookup foreman hostgroup
                    # By definition, hostgroup should be Marca+"_"+Modelo
                    hostgroup_name = switch.modelo.marca.nome + '_' + switch.modelo.nome
                    hostgroups = foreman.hostgroups.index(
                        search=hostgroup_name)
                    if len(hostgroups['results']) == 0:
                        raise RackConfigError(None, rack.nome, 'Could not create entry for %s. Could not find hostgroup %s in foreman.' % (
                            switch.nome, hostgroup_name))
                    elif len(hostgroups['results']) > 1:
                        raise RackConfigError(None, rack.nome, 'Could not create entry for %s. Multiple hostgroups %s found in Foreman.' % (
                            switch.nome, hostgroup_name))
                    else:
                        hostgroup_id = hostgroups['results'][0]['id']

                    host = foreman.hosts.create(host={'name': switch.nome, 'ip': ip, 'mac': mac, 'environment_id': FOREMAN_HOSTS_ENVIRONMENT_ID,
                                                      'hostgroup_id': hostgroup_id, 'subnet_id': subnet_id, 'build': 'true', 'overwrite': 'true'})
                    switch_cadastrado = 1

            if not switch_cadastrado:
                raise RackConfigError(None, rack.nome, "Unknown error. Could not create entry for %s in foreman." % (switch.nome))
    #end - Create Foreman entries for rack switches
    var1 = autoprovision_splf(num_rack, FILEINLF1, FILEINLF2, FILEINSP1, FILEINSP2, FILEINSP3, FILEINSP4,
                              name_lf1, name_lf2, name_oob, name_sp1, name_sp2, name_sp3, name_sp4,
                              ip_mgmtlf1, ip_mgmtlf2,
                              int_oob_mgmtlf1, int_oob_mgmtlf2, int_sp1, int_sp2, int_sp3, int_sp4, int_lf1_sp1,
                              int_lf1_sp2, int_lf2_sp3, int_lf2_sp4)

    var2 = autoprovision_coreoob(num_rack, FILEINCR1, FILEINCR2, FILEINOOB,
                                 name_core1, name_core2, name_oob, name_lf1, name_lf2,
                                 ip_mgmtoob, int_oob_core1, int_oob_core2, int_core1_oob, int_core2_oob )


    if var1 and var2:
        return True

    return False


class RackConfigResource(RestResource):

    log = logging.getLogger('RackConfigResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to create the configuration file.

        URL: rack/gerar-arq-config/id_rack
        """
        try:
            self.log.info('CONFIG')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            rack_id = kwargs.get('id_rack')
            rack = Rack()
            rack = rack.get_by_pk(rack_id)
            var = False

            # Chama o script para gerar os arquivos de configuracao
            var = gera_config(rack)

            rack.__dict__.update(id=rack_id, config=var)
            rack.save()

            success_map = dict()
            success_map['rack_conf'] = var
            map = dict()
            map['sucesso'] = success_map

            return self.response(dumps_networkapi(map))

        except RackConfigError, e:
            return self.response_error(382, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackNumberNotFoundError:
            return self.response_error(379, rack_id)

        except RackError:
            return self.response_error(382)

        except InterfaceNotFoundError:
            return self.response_error(141)

        except ObjectDoesNotExist, exception:
            self.log.error(exception)
            raise var_exceptions.VariableDoesNotExistException()

        except ForemanException, e:
            self.log.error('Error acessing Foreman Server %s' % str(e))
            return self.response_error(391, str(e))

        except RequestException, e:
            return self.response_error(391, e)
