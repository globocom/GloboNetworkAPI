# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.blockrules.models import BlockRules
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
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


def save_or_update(self, request, user, update=False):

    try:
        # User permission
        if not has_perm(user, AdminPermission.VIP_VALIDATION, AdminPermission.WRITE_OPERATION):
            self.log.error(
                u'User does not have permission to perform the operation.')
            raise UserNotAuthorizedError(None)

        # Load XML data
        xml_map, attrs_map = loads(request.raw_post_data)

        # XML data format
        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

        map = networkapi_map.get('map')
        if map is None:
            return self.response_error(3, u'There is no value to the map tag of XML request.')

        environment_id = map['id_env']
        if not is_valid_int_greater_zero_param(environment_id):
            self.log.error(
                u'The environment_id parameter is not a valid value: %s.', environment_id)
            raise InvalidValueError(None, 'environment_id', environment_id)

        environment = Ambiente.get_by_pk(environment_id)

        if update:
            for block in environment.blockrules_set.all():
                block.delete()
        else:
            if environment.blockrules_set.count() > 0:
                return self.response_error(357)

        if 'blocks' in map:
            blocks = map['blocks'] if type(
                map['blocks']) is list else [map['blocks'], ]
            for order, content in enumerate(blocks):

                block = BlockRules()

                block.content = content
                block.order = order
                block.environment = environment

                block.save()

        return self.response(dumps_networkapi({}))

    except AmbienteNotFoundError, e:
        self.log.error('Environment not found')
        return self.response_error(112)
    except InvalidValueError, e:
        self.log.error('Invalid param')
        return self.response_error(269, e.param, e.value)
    except UserNotAuthorizedError:
        return self.not_authorized()
    except XMLError, x:
        self.log.error(u'Error reading the XML request.')
        return self.response_error(3, x)
    except Exception, e:
        self.log.error(e)
        return self.response_error(1)


class EnvironmentBlocks(RestResource):

    log = logging.getLogger('EnvironmentBlocks')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to update Blocks in Environment.

        URL: environment/update_blocks/
        """

        self.log.info('Update blocks in Environment')

        return save_or_update(self, request, user, True)

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to insert Blocks in Environment.

        URL: environment/save_blocks/
        """

        self.log.info('Add blocks in Environment')

        return save_or_update(self, request, user)

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get Blocks in Environment.

        URL: environment/get_blocks/<id_environment>
        """

        try:
            self.log.info('Get blocks in Environment')

            # User permission
            if not has_perm(user, AdminPermission.VIP_VALIDATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data

            id_environment = kwargs.get('environment_id')

            if not is_valid_int_greater_zero_param(id_environment):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.', id_environment)
                raise InvalidValueError(None, 'environment_id', id_environment)

            blocks = BlockRules.objects.filter(
                environment__id=id_environment).order_by('order')

            blocks_list = list()

            for block in blocks:
                blocks_list.append({'content': block.content, 'id': block.id})

            return self.response(dumps_networkapi({'blocks': blocks_list}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except Exception, e:
            self.log.error(e)
            return self.response_error(1)
