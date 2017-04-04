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

from ...base import BasePlugin
from networkapi.infrastructure.script_utils import exec_script
from networkapi.plugins import exceptions as base_exceptions


log = logging.getLogger(__name__)


class ACE(BasePlugin):

    def delete_vip(self, vips):
        try:
            if vips.get('layers'):
                for vip_id in vips.get('layers'):
                    for id_layer in vips.get('layers').get(vip_id):
                        vip_request = vips.get('layers').get(
                            vip_id).get(id_layer).get('vip_request')
                        command = 'gerador_vips -i %s --remove --aceonly' % vip_request[
                            'id']
                        log.info('calling script: %s' % command)
                        code, stdout, stderr = exec_script(command)
        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        pools_del = list()
        return pools_del

    def update_vip(self, vips):
        log.info('bypass')

        pools_ins = list()
        pools_del = list()

        return pools_ins, pools_del

    def create_vip(self, vips):
        try:
            if vips.get('layers'):
                for vip_id in vips.get('layers'):
                    for id_layer in vips.get('layers').get(vip_id):
                        vip_request = vips.get('layers').get(
                            vip_id).get(id_layer).get('vip_request')
                        command = 'gerador_vips -i %s --cria --aceonly' % vip_request[
                            'id']
                        log.info('calling script: %s' % command)
                        code, stdout, stderr = exec_script(command)
        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        pools_ins = list()
        return pools_ins
