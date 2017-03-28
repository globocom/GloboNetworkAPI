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

from networkapi.filter.models import Filter
from networkapi.filter.models import FilterError
from networkapi.models.BaseModel import BaseModel


class FilterEquipTypeDuplicateError(FilterError):

    """Returns exception for FilterEquipType search by filter and equiptype."""

    def __init__(self, cause, message=None):
        FilterError.__init__(self, cause, message)


class CantDissociateError(FilterError):

    """Returns exception when a equip type cant be dissociated."""

    def __init__(self, cause, message=None):
        FilterError.__init__(self, cause, message)


class FilterEquipType(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    filter = models.ForeignKey(Filter, db_column='id_filter')
    equiptype = models.ForeignKey(
        'equipamento.TipoEquipamento', db_column='id_equiptype')

    log = logging.getLogger('FilterEquipType')

    class Meta(BaseModel.Meta):
        db_table = u'filter_equiptype_xref'
        managed = True
        unique_together = ('filter', 'equiptype')

    def validate(self):
        """Validates if EquipType is already associated with Filter

            @raise FilterEquipTypeDuplicateError: if EquipType is already associated with Filter
        """
        try:
            FilterEquipType.objects.get(
                filter=self.filter, equiptype=self.equiptype)
            raise FilterEquipTypeDuplicateError(
                None, u'EquipType already registered for the Filter.')
        except ObjectDoesNotExist:
            pass

    def delete(self):

        from networkapi.ambiente.models import Ambiente
        from networkapi.ip.models import NetworkIPv4, NetworkIPv6, IpEquipamento, Ipv6Equipament
        from networkapi.vlan.models import Vlan
        from django.db.models import Count

        # Get environments using this filter
        envs_using_this_filter = [
            env.id for env in Ambiente.objects.filter(filter=self.filter.id)]

        if len(envs_using_this_filter) > 0:
            # Test if there's filter case 1 and 2, two networks with same ip
            # range or equipment with two ips in networks with same ip range

            # Get filters using this equip type and not this filter
            filters_using_eq_tp = [fet.filter.id for fet in FilterEquipType.objects.filter(
                equiptype=self.equiptype.id).exclude(filter=self.filter.id)]

            # Get environments using other filters
            envs_using_filters = [
                env.id for env in Ambiente.objects.filter(filter__in=filters_using_eq_tp)]

            # Get all networks from environments using this filter, grouped by
            # ip range
            this_filter_nets = NetworkIPv4.objects.filter(vlan__ambiente__in=envs_using_this_filter).values(
                'oct1', 'oct2', 'oct3', 'oct4', 'block').annotate(count=Count('id'))
            for net in this_filter_nets:
                if net['count'] > 1:
                    self.log.error(
                        u'Cannot dissociate filter and equip type because there are two networks with same ip range using filters')
                    raise CantDissociateError(
                        {'equiptype': self.equiptype.tipo_equipamento, 'filter_name': self.filter.name}, u'Cannot dissociate filter and equip type')

            # Get all networks from environments using other filters, grouped
            # by ip range
            other_filter_nets = NetworkIPv4.objects.filter(vlan__ambiente__in=envs_using_filters).values(
                'oct1', 'oct2', 'oct3', 'oct4', 'block').annotate(count=Count('id'))

            for net in this_filter_nets:
                if net in other_filter_nets:
                    self.log.error(
                        u'Cannot dissociate filter and equip type because there are two networks with same ip range using filters')
                    raise CantDissociateError(
                        {'equiptype': self.equiptype.tipo_equipamento, 'filter_name': self.filter.name}, u'Cannot dissociate filter and equip type')

            # Get all networks from environments using this filter, grouped by
            # ip range
            this_filter_nets = NetworkIPv6.objects.filter(vlan__ambiente__in=envs_using_this_filter).values(
                'block1', 'block2', 'block3', 'block4', 'block5', 'block6', 'block7', 'block8', 'block').annotate(count=Count('id'))
            for net in this_filter_nets:
                if net['count'] > 1:
                    self.log.error(
                        u'Cannot dissociate filter and equip type because there are two networks with same ip range using filters')
                    raise CantDissociateError(
                        {'equiptype': self.equiptype.tipo_equipamento, 'filter_name': self.filter.name}, u'Cannot dissociate filter and equip type')

            # Get all networks from environments using other filters, grouped
            # by ip range
            other_filter_nets = NetworkIPv6.objects.filter(vlan__ambiente__in=envs_using_filters).values(
                'block1', 'block2', 'block3', 'block4', 'block5', 'block6', 'block7', 'block8', 'block').annotate(count=Count('id'))

            for net in this_filter_nets:
                if net in other_filter_nets:
                    self.log.error(
                        u'Cannot dissociate filter and equip type because there are two networks with same ip range using filters')
                    raise CantDissociateError(
                        {'equiptype': self.equiptype.tipo_equipamento, 'filter_name': self.filter.name}, u'Cannot dissociate filter and equip type')
            # End of filter test case 1 and 2

            # Filter test case 3
            vlans_in_environments = Vlan.objects.filter(
                ambiente__in=envs_using_this_filter + envs_using_filters).values('num_vlan').annotate(count=Count('id'))

            for vlan_group in vlans_in_environments:
                # Two or more vlans with same number
                if vlan_group['count'] > 1:
                    # Get vlans with same number
                    vlans_same_number = [vlan.id for vlan in Vlan.objects.filter(
                        ambiente__in=envs_using_this_filter + envs_using_filters, num_vlan=vlan_group['num_vlan'])]

                    # Equips for each vlan
                    equips_in_diff_vlans = dict()
                    # All equips from these vlans
                    final_list = list()
                    total_len = 0
                    for vlan_ in vlans_same_number:
                        # Create entry in dict
                        if vlan_ not in equips_in_diff_vlans:
                            equips_in_diff_vlans[vlan_] = list()
                        # Get all equips in networks of vlan
                        for ipeq in IpEquipamento.objects.filter(ip__networkipv4__vlan=vlan_):
                            equips_in_diff_vlans[vlan_].append(
                                ipeq.equipamento.id)
                            final_list.append(ipeq.equipamento.id)
                        # Get all equips in networks v6 of vlan
                        for ipv6eq in Ipv6Equipament.objects.filter(ip__networkipv6__vlan=vlan_):
                            equips_in_diff_vlans[vlan_].append(
                                ipv6eq.equipamento.id)
                            final_list.append(ipv6eq.equipamento.id)

                        total_len = total_len + \
                            len(equips_in_diff_vlans[vlan_])

                    # If any equip is duplicated
                    if len(list(set(final_list))) != total_len:
                        # Get equipments in more than one vlan
                        equips = [
                            eqp for eqp in final_list if final_list.count(eqp) > 1]

                        # Test if these equips are in environments using this
                        # filter
                        if len(IpEquipamento.objects.filter(ip__networkipv4__vlan__ambiente__in=envs_using_this_filter, equipamento__in=equips)) > 0 or \
                                len(Ipv6Equipament.objects.filter(ip__networkipv6__vlan__ambiente__in=envs_using_this_filter, equipamento__in=equips)) > 0:
                            self.log.error(
                                u'Cannot dissociate filter and equip type because there are two vlans with same equipment')
                            raise CantDissociateError(
                                {'equiptype': self.equiptype.tipo_equipamento, 'filter_name': self.filter.name}, u'Cannot dissociate filter and equip type')

            # End of filter test case 3

        super(FilterEquipType, self).delete()
