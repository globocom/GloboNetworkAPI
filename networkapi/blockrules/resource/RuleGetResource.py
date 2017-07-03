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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.auth import has_perm
from networkapi.blockrules.models import BlockRules
from networkapi.blockrules.models import Rule
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class RuleGetResource(RestResource):

    """Treat requests GET to get Rules in Environment.

    URL: environment/rule/all/<id_environment>/
    """

    log = logging.getLogger('RuleResource')

    def handle_get(self, request, user, *args, **kwargs):
        try:
            self.log.info('Get rules in Environment')

            # User permission
            if not has_perm(user, AdminPermission.VIP_VALIDATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_env = kwargs.get('id_env')

            if not is_valid_int_greater_zero_param(id_env):
                self.log.error(
                    u'The id_env parameter is not a valid value: %s.', id_env)
                raise InvalidValueError(None, 'id_env', id_env)

            Ambiente.objects.get(pk=id_env)
            rules = Rule.objects.filter(environment=id_env, vip=None)
            rule_list = []
            for rule in rules:
                rule_list.append(model_to_dict(rule))
            return self.response(dumps_networkapi({'rules': rule_list}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except Exception, e:
            self.log.error(e)
            return self.response_error(1)
