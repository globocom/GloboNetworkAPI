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

from __future__ import with_statement
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import logging
from networkapi.api_network import exceptions
from rest_framework.exceptions import APIException
from networkapi.models.BaseModel import BaseModel
from networkapi.ip.models import Ip, Ipv6, NetworkIPv4, NetworkIPv6
from _mysql_exceptions import OperationalError

class DHCPRelayIPv4(BaseModel):

	log = logging.getLogger('DHCPRelayIPv4')

	id = models.AutoField(primary_key=True, db_column='id_dhcprelay_ipv4')
	ipv4 = models.ForeignKey(Ip, db_column='id_ip')
	networkipv4 = models.ForeignKey(NetworkIPv4, db_column='id_networkipv4')

	class Meta(BaseModel.Meta):
		db_table = u'dhcprelay_ipv4'
		managed = True
		unique_together = ('ipv4', 'networkipv4')

	@classmethod
	def get_by_pk(self, id):
		'''Get DHCPRelayIPv4 by id.

		@return: DHCPRelayIPv4

		@raise DHCPRelayNotFoundError: DHCPRelayIPv4 is not registered.
		@raise OperationalError: Lock wait timeout exceed'''
		
		try:
			return DHCPRelayIPv4.objects.get(id=id)
		except ObjectDoesNotExist, e:
			raise exceptions.DHCPRelayNotFoundError('IPv4', id)
		except OperationalError, e:
			self.log.error(u'Lock wait timeout exceeded searching DHCPRelayIPv4.')
			raise OperationalError(
				e, u'Lock wait timeout exceeded; try restarting transaction')
		except Exception, e:
			self.log.error(u'Failure to search the DHCPRelayIPv4.')
			raise api_exceptions.NetworkAPIException()

class DHCPRelayIPv6(BaseModel):

	log = logging.getLogger('DHCPRelayIPv6')

	id = models.AutoField(primary_key=True, db_column='id_dhcprelay_ipv6')
	ipv6 = models.ForeignKey(Ipv6, db_column='id_ipv6')
	networkipv6 = models.ForeignKey(NetworkIPv6, db_column='id_networkipv6')

	class Meta(BaseModel.Meta):
		db_table = u'dhcprelay_ipv6'
		managed = True
		unique_together = ('ipv6', 'networkipv6')

	def get_by_pk(self, id):
		'''Get DHCPRelayIPv6 by id.

		@return: DHCPRelayIPv6

		@raise DHCPRelayNotFoundError: DHCPRelayIPv6 is not registered.
		@raise OperationalError: Lock wait timeout exceed
		'''
		try:
			return DHCPRelayIPv6.objects.get(id=id)
		except ObjectDoesNotExist, e:
			raise exceptions.DHCPRelayNotFoundError('IPv6', id)
		except OperationalError, e:
			self.log.error(u'Lock wait timeout exceeded searching DHCPRelayIPv6.')
			raise OperationalError(
				e, u'Lock wait timeout exceeded; try restarting transaction')
		except Exception, e:
			self.log.error(u'Failure to search the DHCPRelayIPv6.')
			raise api_exceptions.NetworkAPIException()

