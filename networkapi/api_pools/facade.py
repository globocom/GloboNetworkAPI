# -*- coding:utf-8 -*-

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

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction

from networkapi.api_pools import exceptions
from networkapi.api_pools.models import OptionPool
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.infrastructure.script_utils import exec_script, ScriptError
from networkapi.ip.models import Ipv6, Ip
from networkapi.requisicaovips.models import ServerPoolMember, ServerPool
from networkapi.util import is_valid_int_greater_zero_param, is_valid_list_int_greater_zero_param

from networkapi.ambiente.models import IP_VERSION

from networkapi.log import Log

log = Log(__name__)

#Todo
#Not to be used alone like this
#User has to specifically choose an existing healthcheck in order to use the same healthcheck
#between pools
def get_or_create_healthcheck(user, healthcheck_expect, healthcheck_type, healthcheck_request, healthcheck_destination, identifier=''):
    try:
        # Query HealthCheck table for one equal this
        if identifier == '':
            hc = Healthcheck.objects.get(healthcheck_expect=healthcheck_expect, healthcheck_type=healthcheck_type,
                                     healthcheck_request=healthcheck_request, destination=healthcheck_destination)
        else:
            hc = Healthcheck.objects.get(identifier=identifier, healthcheck_expect=healthcheck_expect, healthcheck_type=healthcheck_type,
                                     healthcheck_request=healthcheck_request, destination=healthcheck_destination)

    # Else, add a new one
    except ObjectDoesNotExist:
        hc = Healthcheck(identifier=identifier, healthcheck_type=healthcheck_type, healthcheck_request=healthcheck_request,
                         healthcheck_expect=healthcheck_expect, destination=healthcheck_destination)
        hc.save(user)

    #Get the fisrt occureny and warn if redundant HCs are present
    except MultipleObjectsReturned, e:
        log.warning("Multiple healthcheck entries found for the given parameters")
        if identifier == '':
            hc = Healthcheck.objects.filter(healthcheck_expect=healthcheck_expect, healthcheck_type=healthcheck_type,
                                         healthcheck_request=healthcheck_request, destination=healthcheck_destination).order_by('id')[0]
        else:
            hc = Healthcheck.objects.filter(identifier=identifier, healthcheck_expect=healthcheck_expect, healthcheck_type=healthcheck_type,
                                         healthcheck_request=healthcheck_request, destination=healthcheck_destination).order_by('id')[0]

    return hc

def save_server_pool(user, id, identifier, default_port, hc, env, balancing, maxconn, id_pool_member, servicedownaction):
    # Save Server pool
    old_healthcheck = None

    if id:
        sp = ServerPool.objects.get(id=id)

        # storage old healthcheck , lb method and service-down-action
        old_servicedownaction = sp.servicedownaction
        old_identifier = sp.identifier
        old_healthcheck = Healthcheck.objects.get(id=sp.healthcheck.id)
        old_lb_method =  sp.lb_method
        old_maxconn = sp.default_limit

        #valid change environment
        if sp.environment and sp.environment.id != env.id:
            if sp.pool_created:
                raise exceptions.UpdateEnvironmentPoolCreatedException()
            del_smp = sp.serverpoolmember_set.exclude(id__in=id_pool_member)
            vip = sp.vipporttopool_set.count()
            if vip > 0:
                raise exceptions.UpdateEnvironmentVIPException()

            if len(del_smp) > 0:
                raise exceptions.UpdateEnvironmentServerPoolMemberException()

        #Pool already created, it is not possible to change Pool Identifier
        if(old_identifier != identifier and sp.pool_created):
            raise exceptions.CreatedPoolIdentifierException()

        sp.default_port = default_port
        sp.environment = env
        sp.default_limit = old_maxconn
        sp.healthcheck = old_healthcheck
        sp.lb_method = old_lb_method
        sp.identifier = identifier
        sp.save(user)

        sp.default_limit = maxconn
        sp.save(user)

        #If exists pool member, checks if all them have the same maxconn
        #before changing default maxconn of pool
        if(len(sp.serverpoolmember_set.all()) > 0):
            if(old_maxconn != sp.default_limit and sp.pool_created):

                for serverpoolmember in sp.serverpoolmember_set.all():
                    if serverpoolmember.limit != old_maxconn:
                        raise exceptions.ScriptAlterLimitPoolDiffMembersException()
                    else:
                        serverpoolmember.limit = maxconn
                        serverpoolmember.save(user)

                transaction.commit()
                command = settings.POOL_MANAGEMENT_LIMITS % (sp.id)
                code, _, _ = exec_script(command)
                if code != 0:
                    sp.default_limit = old_maxconn
                    for serverpoolmember in sp.serverpoolmember_set.all():
                        serverpoolmember.limit = old_maxconn
                        serverpoolmember.save(user)

                    sp.save(user)
                    transaction.commit()
                    raise exceptions.ScriptAlterLimitPoolException()

        #Applies new healthcheck in pool
        #Todo - new method
        sp.healthcheck = hc
        sp.save(user)
        if(old_healthcheck.id != hc.id and sp.pool_created):
            transaction.commit()
            command = settings.POOL_HEALTHCHECK % (sp.id)
            code, _, _ = exec_script(command)
            if code != 0:
                sp.healthcheck = old_healthcheck
                sp.save(user)
                transaction.commit()
                raise exceptions.ScriptCreatePoolException()
            
        #Applies new lb method in pool
        #Todo - new method
        sp.lb_method = balancing
        sp.save(user)
        if(old_lb_method != sp.lb_method and sp.pool_created):
            transaction.commit()
            command = settings.POOL_MANAGEMENT_LB_METHOD % (sp.id)
            code, _, _ = exec_script(command)
            if code != 0:
                sp.lb_method = old_lb_method
                sp.save(user)
                transaction.commit()
                raise exceptions.ScriptCreatePoolException()

        #Applies new service-down-action in pool
        #Todo - new method
        sp.servicedownaction = servicedownaction
        sp.save(user)
        if(old_servicedownaction != sp.servicedownaction and sp.pool_created):
            transaction.commit()
            command = settings.POOL_SERVICEDOWNACTION % (sp.id)
            code, _, _ = exec_script(command)
            if code != 0:
                sp.servicedownaction = old_servicedownaction
                sp.save(user)
                transaction.commit()
                raise exceptions.ScriptAlterServiceDownActionException()

    else:
        sp = ServerPool(identifier=identifier, default_port=default_port, healthcheck=hc,
                        environment=env, pool_created=False, lb_method=balancing, default_limit=maxconn, servicedownaction=servicedownaction)
        sp.save(user)

    return sp, (old_healthcheck.id if old_healthcheck else None)


def prepare_to_save_reals(ip_list_full, ports_reals, nome_equips, priorities, weight, id_pool_member, id_equips):

    list_server_pool_member = list()

    if id_pool_member:

        invalid_ports_real = [i for i in ports_reals if int(i) > 65535 or int(i) < 1]
        invalid_priority = [i for i in priorities if int(i) > 4294967295 or int(i) < 0]

        if invalid_priority:
            raise exceptions.InvalidRealPoolException('O valor da Prioridade deve estar entre 0 e 4294967295.')

        if invalid_ports_real:
            raise exceptions.InvalidRealPoolException('O número da porta deve estar entre 1 e 65535.')

        if len(id_equips) != len(id_pool_member):
            raise exceptions.InvalidRealPoolException('Quantidade de portas e equipamento difere.')

        for i in range(0, len(ip_list_full)):
            for j in range(0, len(ip_list_full)):
                if i == j:
                    pass
                elif ports_reals[i] == ports_reals[j] and ip_list_full[i].get('id', '') == ip_list_full[j].get('id', ''):
                    raise exceptions.InvalidRealPoolException('Ips com portas iguais.')

        for i in range(0, len(id_pool_member)):
            list_server_pool_member.append({'id': ip_list_full[i].get('id', '') if ip_list_full[i] else '',
                                            'ip': ip_list_full[i].get('ip', '') if ip_list_full[i] else '',
                                            'port_real': ports_reals[i],
                                            'nome_equips': nome_equips[i],
                                            'priority': priorities[i],
                                            'weight': weight[i],
                                            'id_pool_member': id_pool_member[i],
                                          })
    return list_server_pool_member


def save_server_pool_member(user, sp, list_server_pool_member):

    list_pool_member = list()
    # Remove empty values from list
    id_pool_member_noempty = [x['id_pool_member'] for x in list_server_pool_member if x['id_pool_member'] != '']

    #exclue server pool member
    del_smp = sp.serverpoolmember_set.exclude(id__in=id_pool_member_noempty)
    if del_smp:
        for obj in del_smp:

            obj.delete(user)

            #execute script remove real if pool already created
            #commit transaction after each successful script call
            if sp.pool_created:
                command = settings.POOL_REAL_REMOVE % (obj.server_pool_id, obj.ip_id if obj.ip else obj.ipv6_id, obj.port_real)
                code, _, _ = exec_script(command)
                if code != 0:
                    raise exceptions.ScriptCreatePoolException()
                transaction.commit()


    if list_server_pool_member:
        for dic in list_server_pool_member:

            ip_object = None
            ipv6_object = None
            if len(dic['ip']) <= 15:
                ip_object = Ip.get_by_pk(dic['id'])

                if sp.environment.divisao_dc.id != ip_object.networkipv4.vlan.ambiente.divisao_dc.id \
                        or sp.environment.ambiente_logico.id != ip_object.networkipv4.vlan.ambiente.ambiente_logico.id:
                    raise exceptions.IpNotFoundByEnvironment()

            else:
                ipv6_object = Ipv6.get_by_pk(dic['id'])

                if sp.environment.divisao_dc.id != ipv6_object.networkipv6.vlan.ambiente.divisao_dc.id \
                        or sp.environment.ambiente_logico.id != ipv6_object.networkipv6.vlan.ambiente.ambiente_logico.id:
                    raise exceptions.IpNotFoundByEnvironment()

            id_pool = sp.id
            id_ip = ip_object and ip_object.id or ipv6_object and ipv6_object.id
            port_ip = dic['port_real']

            if dic['id_pool_member']:
                spm = ServerPoolMember.objects.get(id=dic['id_pool_member'])
                spm.server_pool = sp
                spm.identifier = dic['nome_equips']
                spm.ip = ip_object
                spm.ipv6 = ipv6_object
                spm.priority = dic['priority']
                spm.weight = dic['weight']
                spm.limit = sp.default_limit
                spm.port_real = dic['port_real']

            else:
                spm = ServerPoolMember(server_pool=sp, identifier=dic['nome_equips'], ip=ip_object, ipv6=ipv6_object,
                                       priority=dic['priority'], weight=dic['weight'], limit=sp.default_limit,
                                       port_real=dic['port_real'])

                spm.save(user)

                #execute script to create real if pool already created
                #commits transaction. Rolls back if script returns error
                if sp.pool_created:
                    transaction.commit()
                    #def prepare_and_save(self, server_pool, ip, ip_type, priority, weight, port_real, user, commit=False):
                    #spm.prepare_and_save(sp, ip_object, IP_VERSION.IPv4[1], dic['priority'], dic['weight'], dic['port_real'], user, True)
                    command = settings.POOL_REAL_CREATE % (id_pool, id_ip, port_ip)
                    code, _, _ = exec_script(command)
                    if code != 0:
                        spm.delete(user)
                        transaction.commit()
                        raise exceptions.ScriptCreatePoolException()


            #if sp.healthcheck_id:
            #    spm.healthcheck = sp.healthcheck



            list_pool_member.append(spm)

    return list_pool_member


def exec_script_check_poolmember_by_pool(pool_id):

    #execute script check status real
    command = settings.POOL_REAL_CHECK_BY_POOL % (pool_id)
    status_code, stdout, stderr = exec_script(command)

    if status_code != 0:
        raise exceptions.ScriptCheckStatusPoolMemberException()

    return stdout


def manager_pools(request):
    """
    Manager Status Pool Members Enable/Disabled By Pool

    :param request: HttpRequest

    """

    try:
        pool_id = request.DATA.get("server_pool_id")
        pool_members = request.DATA.get("server_pool_members", [])

        # List to validate pool member status
        valid_status = [0, 1, False, True]

        pool_members_id = [member.get('id') for member in pool_members]

        if not is_valid_int_greater_zero_param(pool_id):
            raise exceptions.InvalidIdPoolException()

        #Validate pool members id
        is_valid_list_int_greater_zero_param(pool_members_id)

        pool_obj = ServerPool.objects.get(id=pool_id)

        related_pool_members = pool_obj.serverpoolmember_set.order_by('id')

        received_pool_members = ServerPoolMember.objects.filter(id__in=pool_members_id).order_by('id')

        relates = list(related_pool_members)
        receives = list(received_pool_members)

        if relates != receives:
            raise exceptions.InvalidIdPoolMemberException(u'Required All Pool Members By Pool')

        for member in pool_members:

            member_id = member.get("id")
            member_status = member.get("status")

            if member_status not in valid_status:
                raise exceptions.InvalidStatusPoolMemberException()

            server_pool_member = ServerPoolMember.objects.get(id=member_id)
            server_pool_member.status = member_status

            server_pool_member.save(request.user, commit=True)

        #Execute Script To Set Status
        command = settings.POOL_MANAGEMENT_MEMBERS_STATUS % pool_id
        code, _, _ = exec_script(command)
        if code != 0:
            raise exceptions.ScriptManagementPoolException()

    except (exceptions.ScriptManagementPoolException, ScriptError), exception:

        # Rollback
        for old_member in related_pool_members:
            old_member.save(request.user, commit=True)

        raise exception


def save_option_pool(user, type, description):


    '''if id:
        sp = OptionPool.objects.get(id=id)

        sp.type = type
        sp.description = description
        sp.save(user)


    else:'''

    sp = OptionPool(type=type, name=description)
    sp.save(user)

    return sp
