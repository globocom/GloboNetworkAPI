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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError


class VlanListResource(RestResource):

    log = logging.getLogger('VlanListResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles POST requests to list all VLANs.

        URLs: /vlan/all/
        """

        self.log.info('List all VLANs')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Rules

            vlans = Vlan.objects.select_related(
                'ambiente',
                'divisao_dc',
                'ambiente_logico',
                'grupo_l3'
            ).all()

            vlan_list = []

            for vlan in vlans:
                model_dict = dict()
                model_dict['id'] = vlan.id
                model_dict['name'] = vlan.nome
                model_dict['num_vlan'] = vlan.num_vlan
                model_dict['environment'] = vlan.ambiente.divisao_dc.nome + ' - ' + \
                    vlan.ambiente.ambiente_logico.nome + \
                    ' - ' + vlan.ambiente.grupo_l3.nome

                vlan_list.append(model_dict)

            return self.response(dumps_networkapi({'vlan': vlan_list}))

        except (VlanError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
        except BaseException, e:
            self.log.error(e)
            return self.response_error(1)
