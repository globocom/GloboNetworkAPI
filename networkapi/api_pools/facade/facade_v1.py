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

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from networkapi.ambiente.models import Ambiente
from networkapi.api_pools import exceptions
from networkapi.api_pools.models import OptionPool
from networkapi.api_pools.models import OptionPoolEnvironment
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_list_int_greater_zero_param

log = logging.getLogger(__name__)


# Todo
# Not to be used alone like this
# User has to specifically choose an existing healthcheck in order to use the same healthcheck
# between pools
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
        hc.save()

    # Get the fisrt occureny and warn if redundant HCs are present
    except MultipleObjectsReturned:
        log.warning(
            'Multiple healthcheck entries found for the given parameters')
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

        # store old healthcheck,lb method and service-down-action
        old_servicedownaction = sp.servicedownaction
        old_identifier = sp.identifier
        old_healthcheck = Healthcheck.objects.get(id=sp.healthcheck.id)
        old_lb_method = sp.lb_method
        old_maxconn = sp.default_limit

        # validate change of environment
        if sp.environment and sp.environment.id != env.id:
            validate_change_of_environment(id_pool_member, sp)

        # Pool already created, it is not possible to change Pool Identifier
        if(old_identifier != identifier and sp.pool_created):
            raise exceptions.CreatedPoolIdentifierException()

        update_pool_fields(default_port, env, identifier,
                           old_healthcheck, old_lb_method, old_maxconn, sp, user)

        update_pool_maxconn(maxconn, old_maxconn, sp, user)

        apply_health_check(hc, old_healthcheck, sp, user)

        update_load_balancing_method(balancing, old_lb_method, sp, user)

        apply_service_down_action(
            old_servicedownaction, servicedownaction, sp, user)
    else:
        sp = ServerPool(identifier=identifier, default_port=default_port, healthcheck=hc,
                        environment=env, pool_created=False, lb_method=balancing, default_limit=maxconn, servicedownaction=servicedownaction)
        sp.save()

    return sp, (old_healthcheck.id if old_healthcheck else None)


def update_pool_fields(default_port, env, identifier, old_healthcheck, old_lb_method, old_maxconn, sp, user):
    sp.default_port = default_port
    sp.environment = env
    sp.default_limit = old_maxconn
    sp.healthcheck = old_healthcheck
    sp.lb_method = old_lb_method
    sp.identifier = identifier
    sp.save()


def validate_change_of_environment(id_pool_member, sp):
    if sp.pool_created:
        raise exceptions.UpdateEnvironmentPoolCreatedException()
    del_smp = sp.serverpoolmember_set.exclude(id__in=id_pool_member)
    vip = sp.vipporttopool_set.count()
    if vip > 0:
        raise exceptions.UpdateEnvironmentVIPException()
    if len(del_smp) > 0:
        raise exceptions.UpdateEnvironmentServerPoolMemberException()


def update_pool_maxconn(maxconn, old_maxconn, sp, user):
    sp.default_limit = maxconn
    sp.save()

    # If pool member  exists, checks if all of them have the same maxconn
    # before changing its default maxconn
    if(len(sp.serverpoolmember_set.all()) > 0):
        if(old_maxconn != sp.default_limit and sp.pool_created):

            for serverpoolmember in sp.serverpoolmember_set.all():
                if serverpoolmember.limit != old_maxconn:
                    raise exceptions.ScriptAlterLimitPoolDiffMembersException()
                else:
                    serverpoolmember.limit = maxconn
                    serverpoolmember.save()

            transaction.commit()
            command = settings.POOL_MANAGEMENT_LIMITS % (sp.id)
            code, _, _ = exec_script(command)
            if code != 0:
                sp.default_limit = old_maxconn
                for serverpoolmember in sp.serverpoolmember_set.all():
                    serverpoolmember.limit = old_maxconn
                    serverpoolmember.save()

                sp.save()
                transaction.commit()
                raise exceptions.ScriptAlterLimitPoolException()


def apply_health_check(hc, old_healthcheck, sp, user):
    # Applies new healthcheck in pool
    sp.healthcheck = hc
    sp.save()
    if (old_healthcheck.id != hc.id and sp.pool_created):
        transaction.commit()
        command = settings.POOL_HEALTHCHECK % (sp.id)
        code, _, _ = exec_script(command)
        if code != 0:
            sp.healthcheck = old_healthcheck
            sp.save()
            transaction.commit()
            raise exceptions.ScriptCreatePoolException()


def apply_service_down_action(old_servicedownaction, servicedownaction, sp, user):
    # Applies new service-down-action in pool
    sp.servicedownaction = servicedownaction
    sp.save()
    if (old_servicedownaction != sp.servicedownaction and sp.pool_created):
        transaction.commit()
        command = settings.POOL_SERVICEDOWNACTION % (sp.id)
        code, _, _ = exec_script(command)
        if code != 0:
            sp.servicedownaction = old_servicedownaction
            sp.save()
            transaction.commit()
            raise exceptions.ScriptAlterServiceDownActionException()


def update_load_balancing_method(balancing, old_lb_method, sp, user):
    sp.lb_method = balancing
    sp.save()
    if (old_lb_method != sp.lb_method and sp.pool_created):
        transaction.commit()
        command = settings.POOL_MANAGEMENT_LB_METHOD % (sp.id)
        code, _, _ = exec_script(command)
        if code != 0:
            sp.lb_method = old_lb_method
            sp.save()
            transaction.commit()
            raise exceptions.ScriptCreatePoolException()


def prepare_to_save_reals(ip_list_full, ports_reals, nome_equips, priorities, weight, id_pool_member, id_equips):

    list_server_pool_member = list()

    if id_pool_member:

        invalid_ports_real = [
            i for i in ports_reals if int(i) > 65535 or int(i) < 1]
        invalid_priority = [
            i for i in priorities if int(i) > 4294967295 or int(i) < 0]

        if invalid_priority:
            raise exceptions.InvalidRealPoolException(
                'O valor da Prioridade deve estar entre 0 e 4294967295.')

        if invalid_ports_real:
            raise exceptions.InvalidRealPoolException(
                'O número da porta deve estar entre 1 e 65535.')

        if len(id_equips) != len(id_pool_member):
            raise exceptions.InvalidRealPoolException(
                'Quantidade de portas e equipamento difere.')

        for i in range(0, len(ip_list_full)):
            for j in range(0, len(ip_list_full)):
                if i == j:
                    pass
                elif ports_reals[i] == ports_reals[j] and ip_list_full[i].get('id', '') == ip_list_full[j].get('id', ''):
                    raise exceptions.InvalidRealPoolException(
                        'Ips com portas iguais.')

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


def save_server_pool_member(user, pool, list_server_pool_member):

    list_pool_member = list()
    old_priorities_list = list()

    pool_members_to_be_removed = get_pool_members_to_be_removed(
        list_server_pool_member)
    remove_pool_members(pool_members_to_be_removed, pool, user)

    if list_server_pool_member:
        apply_new_priorities = False

        for dic in list_server_pool_member:
            ip_object, ipv6_object = get_ip_objects(dic)

            pool_member_id = dic['id_pool_member']
            if pool_member_id:
                pool_member = ServerPoolMember.objects.get(id=pool_member_id)
                old_member_priority = pool_member.priority
                old_priorities_list.append(old_member_priority)

                update_pool_member(
                    pool, pool_member, dic, ip_object, ipv6_object, user)

                if(old_member_priority != pool_member.priority and pool.pool_created):
                    apply_new_priorities = True
            else:
                pool_member = ServerPoolMember()
                update_pool_member(
                    pool, pool_member, dic, ip_object, ipv6_object, user)
                pool_member.save()

                old_priorities_list.append(dic['priority'])

                # execute script to create real if pool already created
                # commits transaction. Rolls back if script returns error
                if pool.pool_created:
                    ip_id = ip_object and ip_object.id or ipv6_object and ipv6_object.id
                    deploy_pool_member_config(
                        ip_id, pool.id, dic['port_real'], pool_member, user)

            list_pool_member.append(pool_member)

        # Applies new priority in pool - only 1 script run for all members
        if(apply_new_priorities):
            apply_priorities(list_pool_member, old_priorities_list, pool, user)

    return list_pool_member


def update_pool_member(pool, pool_member, dic, ip_object, ipv6_object, user):
    pool_member.server_pool = pool
    pool_member.limit = pool.default_limit
    pool_member.ip = ip_object
    pool_member.ipv6 = ipv6_object
    pool_member.identifier = dic['nome_equips']
    pool_member.weight = dic['weight']
    pool_member.priority = dic['priority']
    pool_member.port_real = dic['port_real']
    pool_member.save()


def get_ip_objects(dic):
    ip_object = None
    ipv6_object = None
    if len(dic['ip']) <= 15:
        ip_object = Ip.get_by_pk(dic['id'])
    else:
        ipv6_object = Ipv6.get_by_pk(dic['id'])
    return ip_object, ipv6_object


def get_pool_members_to_be_removed(list_server_pool_member):
    # Remove empty values from list
    return [x['id_pool_member'] for x in list_server_pool_member if x['id_pool_member'] != '']


def remove_pool_members(id_pool_member_noempty, sp, user):
    # exclue server pool member
    del_smp = sp.serverpoolmember_set.exclude(id__in=id_pool_member_noempty)
    if del_smp:
        for obj in del_smp:

            obj.delete()

            # execute script remove real if pool already created
            # commit transaction after each successful script call
            if sp.pool_created:
                command = settings.POOL_REAL_REMOVE % (
                    obj.server_pool_id, obj.ip_id if obj.ip else obj.ipv6_id, obj.port_real)
                code, _, _ = exec_script(command)
                if code != 0:
                    raise exceptions.ScriptCreatePoolException()
                transaction.commit()


def deploy_pool_member_config(id_ip, id_pool, port_ip, spm, user):
    transaction.commit()
    # def prepare_and_save(self, server_pool, ip, ip_type, priority, weight, port_real, user, commit=False):
    # spm.prepare_and_save(sp, ip_object, IP_VERSION.IPv4[1], dic['priority'], dic['weight'], dic['port_real'], user, True)
    command = settings.POOL_REAL_CREATE % (id_pool, id_ip, port_ip)
    code, _, _ = exec_script(command)
    if code != 0:
        spm.delete()
        transaction.commit()
        raise exceptions.ScriptCreatePoolException()

        # if sp.healthcheck_id:
        #    spm.healthcheck = sp.healthcheck


def apply_priorities(list_pool_member, old_priorities_list, sp, user):
    transaction.commit()
    command = settings.POOL_MEMBER_PRIORITIES % (sp.id)
    code, _, _ = exec_script(command)
    if code != 0:
        for i in range(0, len(old_priorities_list)):
            list_pool_member[i].priority = old_priorities_list[i]
            list_pool_member[i].save()
        transaction.commit()
        raise exceptions.ScriptAlterPriorityPoolMembersException()


def exec_script_check_poolmember_by_pool(pool_id):

    # execute script check status real
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
        pool_id = request.DATA.get('server_pool_id')
        pool_members = request.DATA.get('server_pool_members', [])

        # List to validate pool member status
        valid_status = [0, 1, False, True]

        pool_members_id = [member.get('id') for member in pool_members]

        if not is_valid_int_greater_zero_param(pool_id):
            raise exceptions.InvalidIdPoolException()

        # Validate pool members id
        is_valid_list_int_greater_zero_param(pool_members_id)

        pool_obj = ServerPool.objects.get(id=pool_id)

        related_pool_members = pool_obj.serverpoolmember_set.order_by('id')

        received_pool_members = ServerPoolMember.objects.filter(
            id__in=pool_members_id).order_by('id')

        relates = list(related_pool_members)
        receives = list(received_pool_members)

        if relates != receives:
            raise exceptions.InvalidIdPoolMemberException(
                u'Required All Pool Members By Pool')

        for member in pool_members:

            member_id = member.get('id')
            member_status = member.get('status')

            if member_status not in valid_status:
                raise exceptions.InvalidStatusPoolMemberException()

            server_pool_member = ServerPoolMember.objects.get(id=member_id)
            server_pool_member.status = member_status

            server_pool_member.save(request.user, commit=True)

        # Execute Script To Set Status
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
    """if id:
        sp = OptionPool.objects.get(id=id)

        sp.type = type
        sp.description = description
        sp.save()


    else:"""

    sp = OptionPool(type=type, name=description)
    sp.save()

    return sp


def update_option_pool(user, option_id, type, description):

    sp = OptionPool.objects.get(id=option_id)

    sp.type = type
    sp.name = description

    sp.save()

    return sp


def delete_option_pool(user, option_id):

    pool_option = OptionPool.objects.get(id=option_id)

    environment_options = OptionPoolEnvironment.objects.all()
    environment_options = environment_options.filter(option=option_id)

    for eop in environment_options:
        eop.delete()

    pool_option.delete()

    return option_id


def save_environment_option_pool(user, option_id, environment_id):

    op = OptionPool.objects.get(id=option_id)
    env = Ambiente.objects.get(id=environment_id)


#    log.warning("objetos buscados %s %s", serializer_options.data, serializer_env.data)

    ope = OptionPoolEnvironment()

    ope.environment = env
    ope.option = op
    ope.save()

    return ope


def update_environment_option_pool(user, environment_option_id, option_id, environment_id):

    ope = OptionPoolEnvironment.objects.get(id=environment_option_id)
    op = OptionPool.objects.get(id=option_id)
    env = Ambiente.objects.get(id=environment_id)

    ope.option = op
    ope.environment = env

    ope.save()

    return ope


def delete_environment_option_pool(user, environment_option_id):

    ope = OptionPoolEnvironment.objects.get(id=environment_option_id)
    ope.delete()

    return environment_option_id
