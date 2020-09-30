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
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from networkapi.plugins.base import BasePlugin
from networkapi.plugins import exceptions
from networkapi.equipamento.models import EquipamentoAcesso

log = logging.getLogger(__name__)


class Junos(BasePlugin):

    # The default ssh port connection is 830:
    # https://www.juniper.net/documentation/en_US/junos-pyez/topics/task/program/junos-pyez-connection-methods.html
    connect_port = 830

    def connect(self):
        """
        Return a connection object
        """

        # Collect the credentials (user and password)
        if self.equipment_access is None:
            try:
                self.equipment_access = EquipamentoAcesso.search(
                    None, self.equipment, 'ssh').uniqueResult()
            except Exception:
                log.error('Access type %s not found for equipment %s.' % ('ssh', self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()
        device = self.equipment_access.fqdn
        username = self.equipment_access.user
        password = self.equipment_access.password

        try:
            self.remote_conn = Device(host=device, user=username, passwd=password, port=self.connect_port)
            self.remote_conn.open()
        except ConnectError as e:
            log.error('Could not connect to juniper host %s: %s' % (device, e))
        except IOError, e:
            log.error('Could not connect to host %s: %s' % (device, e))
            raise exceptions.ConnectionException(device)
        except Exception, e:
            log.error('Error connecting to host %s: %s' % (device, e))
            raise Exception(e)

    def close(self):
        self.remote_conn.close()

    def copyScriptFileToConfig(self, filename, use_vrf='', destination=''):
        pass

    def create_svi(self, svi_number, svi_description='no description'):
        pass

    def ensure_privilege_level(self, privilege_level=None):
        pass

    def remove_svi(self, svi_number):
        pass

    def get_state_member(self, status):
        pass

    def set_state_member(self, status):
        pass

    def create_member(self, status):
        pass

    def remove_member(self, status):
        pass

    def get_restrictions(self, status):
        pass

    def partial_update_vip(self, **kwargs):
        pass

    def get_name_eqpt(self, **kwargs):
        pass

    def update_pool(self, **kwargs):
        pass

    def create_pool(self, **kwargs):
        pass

    def delete_pool(self, **kwargs):
        pass
