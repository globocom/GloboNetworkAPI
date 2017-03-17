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

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count

from networkapi.exception import InvalidValueError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.models.BaseModel import BaseModel
from networkapi.util import clone
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_text


class FilterError(Exception):

    """An error occurred during Filter table access."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class FilterNotFoundError(FilterError):

    """Returns exception for Filter search by pk."""

    def __init__(self, cause, message=None):
        FilterError.__init__(self, cause, message)


class FilterDuplicateError(FilterError):

    """Returns exception for Filter name already existing."""

    def __init__(self, cause, message=None):
        FilterError.__init__(self, cause, message)


class CannotDissociateFilterError(FilterError):

    """Returns exception for Filter in use in environment, cannot be dissociated."""

    def __init__(self, cause, message=None):
        FilterError.__init__(self, cause, message)


class Filter(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_filter')
    name = models.CharField(
        max_length=100, blank=False, unique=True, db_column='name')
    description = models.CharField(
        max_length=200, null=True, blank=True, db_column='description')

    log = logging.getLogger('Filter')

    class Meta(BaseModel.Meta):
        db_table = u'filter'
        managed = True

    @classmethod
    def get_by_pk(cls, id_):
        """"Get Filter by id.

        @return: Filter.

        @raise FilterNotFoundError: Filter is not registered.
        @raise FilterError: Failed to search for the Filter.
        """
        try:
            return Filter.objects.get(pk=id_)
        except ObjectDoesNotExist, e:
            raise FilterNotFoundError(
                e, u'There is no Filter with pk = %s.' % id_)
        except Exception, e:
            cls.log.error(u'Failure to search the filter.')
            raise FilterError(e, u'Failure to search the filter.')

    def delete(self):
        """Override Django's method to remove filter

        Before removing the filter removes all relationships with equipment type.
        """

        # Remove all Filter and TipoEquipamento relations
        for filter_equiptype in self.filterequiptype_set.all():
            filter_equiptype.delete()

        super(Filter, self).delete()

    def validate_filter(self, filter_map):
        """Validates filter fields before add

        @param filter_map: Map with the data of the request.

        @raise InvalidValueError: Represents an error occurred validating a value.
        """

        # Get XML data
        name = filter_map['name']
        description = filter_map['description']

        # name can NOT be greater than 100
        if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100) or not is_valid_text(name):
            self.log.error(u'Parameter name is invalid. Value: %s.', name)
            raise InvalidValueError(None, 'name', name)

        # description can NOT be greater than 200
        if not is_valid_string_minsize(description, 3, False) or not is_valid_string_maxsize(description, 200, False) or not is_valid_text(description, True):
            self.log.error(
                u'Parameter description is invalid. Value: %s.', description)
            raise InvalidValueError(None, 'description', description)

        # Verify existence
        if len(Filter.objects.filter(name=name).exclude(id=self.id)) > 0:
            raise FilterDuplicateError(
                None, u'Já existe um filtro com o nome %s no banco de dados.' % name)

        # set variables
        self.name = name
        self.description = description


def check_filter_use(new_filter_id, env):

    from networkapi.equipamento.models import EquipamentoAmbiente
    from networkapi.ip.models import NetworkIPv4, NetworkIPv6
    from networkapi.vlan.models import Vlan

    try:
        # Check existence of new filter
        new_fil = Filter.objects.get(pk=new_filter_id)
    except ObjectDoesNotExist:
        new_fil = None
        pass

    # Filters
    old_fil = env.filter

    if old_fil is not None:

        # Envs using old filter
        envs_old_filter = old_fil.ambiente_set.all()

        # Vlans in listed envs
        vlans = list()
        for env_old_filter in envs_old_filter:
            for vlan in env_old_filter.vlan_set.all():
                vlans.append(vlan)

        # Nets in vlan
        nets_ipv4 = list()
        nets_ipv6 = list()
        for vlan in vlans:
            for net in vlan.networkipv4_set.all():
                nets_ipv4.append({'net': net, 'vlan_env': vlan.ambiente})
            for net in vlan.networkipv6_set.all():
                nets_ipv6.append({'net': net, 'vlan_env': vlan.ambiente})

        # Verify subnet ipv4
        for i in range(0, len(nets_ipv4)):
            net = nets_ipv4[i].get('net')
            ip = '%s.%s.%s.%s/%s' % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
            network_ip_verify = IPNetwork(ip)

            nets_ipv4_aux = clone(nets_ipv4)
            nets_ipv4_aux.remove(nets_ipv4[i])

            if verify_subnet_and_equip(nets_ipv4_aux, network_ip_verify, 'v4',
                                       net, nets_ipv4[i].get('vlan_env')):
                env_aux_id = nets_ipv4[i].get('vlan_env').id
                if env.id == env_aux_id:
                    raise CannotDissociateFilterError(
                        old_fil.name, u'Filter %s cannot be dissociated, its in use.' % old_fil.name)

        # Verify subnet ipv6
        for i in range(0, len(nets_ipv6)):
            net = nets_ipv6[i].get('net')
            ip = '%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6,
                                                 net.block7, net.block8, net.block)
            network_ip_verify = IPNetwork(ip)

            nets_ipv6_aux = clone(nets_ipv6)
            nets_ipv6_aux.remove(nets_ipv6[i])

            if verify_subnet_and_equip(nets_ipv6_aux, network_ip_verify, 'v6',
                                       net, nets_ipv6[i].get('vlan_env')):
                env_aux_id = nets_ipv6[i].get('vlan_env').id
                if env.id == env_aux_id:
                    raise CannotDissociateFilterError(
                        old_fil.name, u'Filter %s cannot be dissociated, its in use.' % old_fil.name)

        old_tp_equips = [
            fet.equiptype.id for fet in old_fil.filterequiptype_set.all()]
        if new_fil is not None:
            new_tp_equips = [
                fet.equiptype.id for fet in new_fil.filterequiptype_set.all()]
        else:
            new_tp_equips = []

        # EquipTypes being excluded, check for these in environments
        diff_tp_equips = list(set(old_tp_equips) - set(new_tp_equips))

        # Check equipments with type in diff, associated to this environment
        if len(diff_tp_equips) > 0:

            # Filter case 1 and 2

            # Check for networks with same ip range
            nets_same_range = NetworkIPv4.objects.values(
                'oct1', 'oct2', 'oct3', 'oct4', 'block'
            ).annotate(count=Count('id')).filter(count__gt=1)

            if len(nets_same_range) > 0:
                for net_gp in nets_same_range:
                    nets_current_range = NetworkIPv4.objects.filter(
                        oct1=net_gp['oct1'],
                        oct2=net_gp['oct2'],
                        oct3=net_gp['oct3'],
                        oct4=net_gp['oct4'],
                        block=net_gp['block']
                    )
                    envs_of_nets = [
                        net_crt.vlan.ambiente.id for net_crt in nets_current_range]
                    if env.id in envs_of_nets:

                        eqas = EquipamentoAmbiente.objects.filter(
                            equipamento__tipo_equipamento__in=diff_tp_equips, ambiente=env.id)
                        equips_in_env = [eqa.equipamento.id for eqa in eqas]

                        # Get other environments with these equips
                        other_envs = [eqa.ambiente.id for eqa in EquipamentoAmbiente.objects.filter(
                            equipamento__in=equips_in_env,
                            ambiente__in=envs_of_nets
                        ).exclude(ambiente=env.id)]

                        if len(other_envs) > 0:
                            raise CannotDissociateFilterError(
                                old_fil.name, u'Filter %s cannot be dissociated, its in use.' % old_fil.name)

            # Check for networks v6 with same ip range
            nets_same_range_v6 = NetworkIPv6.objects.values(
                'block1', 'block2', 'block3', 'block4',
                'block5', 'block6', 'block7', 'block8', 'block'
            ).annotate(count=Count('id')).filter(count__gt=1)

            if len(nets_same_range_v6) > 0:
                for net_gp in nets_same_range_v6:
                    nets_current_range = NetworkIPv6.objects.filter(
                        block1=net_gp['block1'],
                        block2=net_gp['block2'],
                        block3=net_gp['block3'],
                        block4=net_gp['block4'],
                        block5=net_gp['block5'],
                        block6=net_gp['block6'],
                        block7=net_gp['block7'],
                        block8=net_gp['block8'],
                        block=net_gp['block']
                    )
                    envs_of_nets = [
                        net_crt.vlan.ambiente.id for net_crt in nets_current_range]
                    if env.id in envs_of_nets:

                        eqas = EquipamentoAmbiente.objects.filter(
                            equipamento__tipo_equipamento__in=diff_tp_equips, ambiente=env.id)
                        equips_in_env = [eqa.equipamento.id for eqa in eqas]

                        # Get other environments with these equips
                        other_envs = [eqa.ambiente.id for eqa in EquipamentoAmbiente.objects.filter(
                            equipamento__in=equips_in_env,
                            ambiente__in=envs_of_nets
                        ).exclude(ambiente=env.id)]

                        if len(other_envs) > 0:
                            raise CannotDissociateFilterError(
                                old_fil.name, u'Filter %s cannot be dissociated, its in use.' % old_fil.name)

            # End of filter case 1 and 2

            # Filter case 3

            # Get vlans with same number
            vlans_same_number = Vlan.objects.values('num_vlan').annotate(
                count=Count('id')).filter(count__gt=1)

            if len(vlans_same_number) > 0:
                for vlan_gp in vlans_same_number:
                    vlans_current_number = Vlan.objects.filter(
                        num_vlan=vlan_gp['num_vlan'])
                    envs_of_vlans = [
                        vlan.ambiente.id for vlan in vlans_current_number]

                    if env.id in envs_of_vlans:

                        eqas = EquipamentoAmbiente.objects.filter(
                            ambiente=env.id)
                        equips_in_env = [eqa.equipamento.id for eqa in eqas]

                        # Get other environments with these equips
                        other_envs = [eqa.ambiente.id for eqa in EquipamentoAmbiente.objects.filter(
                            equipamento__in=equips_in_env,
                            ambiente__in=envs_of_vlans
                        ).exclude(ambiente=env.id)]

                        if len(other_envs) > 0:
                            raise CannotDissociateFilterError(
                                old_fil.name, u'Filter %s cannot be dissociated, its in use.' % old_fil.name)

    env.filter = new_fil
    return env
    # End of filters


def verify_subnet_and_equip(vlan_net, network_ip, version, net_obj, env_obj):

    # Check if an equipment is shared in a subnet

    equip_list = get_equips(net_obj, env_obj)

    # One vlan may have many networks, iterate over it
    for net_env in vlan_net:

        net = net_env.get('net')
        env = net_env.get('vlan_env')
        if version == 'v4':
            ip = '%s.%s.%s.%s/%s' % (net.oct1, net.oct2, net.oct3,
                                     net.oct4, net.block)
        else:
            ip = '%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6,
                                                 net.block7, net.block8, net.block)

        ip_net = IPNetwork(ip)
        # If some network, inside this vlan, is subnet of network search param
        if ip_net in network_ip:
            equip_list_aux = get_equips(net, env)

            if len(set(equip_list) & set(equip_list_aux)) > 0:
                # This vlan must be in vlans founded, dont need to continue
                # checking
                return True
        # If some network, inside this vlan, is supernet of network search
        # param
        if network_ip in ip_net:
            equip_list_aux = get_equips(net, env)
            if len(set(equip_list) & set(equip_list_aux)) > 0:
                # This vlan must be in vlans founded, dont need to continue
                # checking
                return True

    # If dont found any subnet return None
    return False


def get_equips(net_obj, env_obj):
    equip_list = list()

    for equip in env_obj.equipamentoambiente_set.all():
        if equip.equipamento_id not in equip_list:
            equip_list.append(equip.equipamento_id)

    try:
        for ip in net_obj.ip_set.all():
            for equip in ip.ipequipamento_set.all():
                if equip.id not in equip_list:
                    equip_list.append(equip.id)
    except:
        for ip in net_obj.ipv6_set.all():
            for equip in ip.ipv6equipament_set.all():
                if equip.id not in equip_list:
                    equip_list.append(equip.id)

    return equip_list
