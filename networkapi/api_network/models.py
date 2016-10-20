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
from __future__ import with_statement

import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model

from networkapi.api_network import exceptions
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.models.BaseModel import BaseModel
# from networkapi.ip.models import Ip
# from networkapi.ip.models import Ipv6
# from networkapi.ip.models import NetworkIPv4
# from networkapi.ip.models import NetworkIPv6


class DHCPRelayIPv4(BaseModel):

    log = logging.getLogger('DHCPRelayIPv4')

    id = models.AutoField(
        primary_key=True,
        db_column='id_dhcprelay_ipv4'
    )
    ipv4 = models.ForeignKey(
        'ip.Ip',
        db_column='id_ip'
    )
    networkipv4 = models.ForeignKey(
        'ip.NetworkIPv4',
        db_column='id_networkipv4'
    )

    class Meta(BaseModel.Meta):
        db_table = u'dhcprelay_ipv4'
        managed = True
        unique_together = ('ipv4', 'networkipv4')

    def create(self, ipv4_id, networkipv4_id):
        ipv4_model = get_model('ip', 'Ipv6')
        networkipv4_model = get_model('ip', 'NetworkIPv6')

        ipv4 = ipv4_model.get_by_pk(ipv4_id)
        networkipv4 = networkipv4_model.get_by_pk(networkipv4_id)

        if len(DHCPRelayIPv4.objects.filter(ipv4=ipv4, networkipv4=networkipv4)) > 0:
            raise exceptions.DHCPRelayAlreadyExistsError(
                ipv4_id, networkipv4_id)

        self.ipv4 = ipv4
        self.networkipv4 = networkipv4

    @classmethod
    def get_by_pk(cls, id):
        """
        Get DHCPRelayIPv4 by id.

        @return: DHCPRelayIPv4

        @raise DHCPRelayNotFoundError: DHCPRelayIPv4 is not registered.
        @raise OperationalError: Lock wait timeout exceed
        """

        try:
            return DHCPRelayIPv4.objects.get(id=id)
        except ObjectDoesNotExist, e:
            raise exceptions.DHCPRelayNotFoundError('IPv4', id)
        except OperationalError, e:
            cls.log.error(
                u'Lock wait timeout exceeded searching DHCPRelayIPv4.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the DHCPRelayIPv4.')
            raise api_exceptions.NetworkAPIException()


class DHCPRelayIPv6(BaseModel):

    log = logging.getLogger('DHCPRelayIPv6')

    id = models.AutoField(
        primary_key=True,
        db_column='id_dhcprelay_ipv6'
    )
    ipv6 = models.ForeignKey(
        'ip.Ipv6',
        db_column='id_ipv6'
    )
    networkipv6 = models.ForeignKey(
        'ip.NetworkIPv6',
        db_column='id_networkipv6'
    )

    class Meta(BaseModel.Meta):
        db_table = u'dhcprelay_ipv6'
        managed = True
        unique_together = ('ipv6', 'networkipv6')

    def create(self, ipv6_id, networkipv6_id):
        ipv6_model = get_model('ip', 'Ipv6')
        networkipv6_model = get_model('ip', 'NetworkIPv6')
        ipv6 = ipv6_model.get_by_pk(ipv6_id)
        networkipv6 = networkipv6_model.get_by_pk(networkipv6_id)

        if len(DHCPRelayIPv6.objects.filter(ipv6=ipv6, networkipv6=networkipv6)) > 0:
            raise exceptions.DHCPRelayAlreadyExistsError(
                ipv6_id, networkipv6_id)

        self.ipv6 = ipv6
        self.networkipv6 = networkipv6

    @classmethod
    def get_by_pk(cls, id):
        """
        Get DHCPRelayIPv6 by id.

        @return: DHCPRelayIPv6

        @raise DHCPRelayNotFoundError: DHCPRelayIPv6 is not registered.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return DHCPRelayIPv6.objects.get(id=id)
        except ObjectDoesNotExist, e:
            raise exceptions.DHCPRelayNotFoundError('IPv6', id)
        except OperationalError, e:
            cls.log.error(
                u'Lock wait timeout exceeded searching DHCPRelayIPv6.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the DHCPRelayIPv6.')
            raise api_exceptions.NetworkAPIException()
