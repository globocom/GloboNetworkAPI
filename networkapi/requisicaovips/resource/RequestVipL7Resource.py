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
from networkapi.blockrules.models import Rule
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.rest import RestResource
from networkapi.util import convert_boolean_to_int
from networkapi.util import is_valid_int_greater_zero_param


class RequestVipL7Resource(RestResource):
    log = logging.getLogger('RequestVipL7Resource')

    def handle_put(self, request, user, *args, **kwargs):
        """ Handles a PUT request to edit the L7 filter.

        URL: vip/<id_vip>/filter/
        """

        if not has_perm(user,
                        AdminPermission.VIP_ALTER_SCRIPT,
                        AdminPermission.WRITE_OPERATION):
            return self.not_authorized()

        id_vip = kwargs.get('id_vip')

        # Load XML data
        xml_map, attrs_map = loads(request.raw_post_data)

        # XML data format
        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'There is no value to the networkapi tag of XML request.')
        vip_map = networkapi_map.get('vip')
        if vip_map is None:
            return self.response_error(3, u'There is no value to the vip tag of XML request.')

        vip = RequisicaoVips.get_by_pk(id_vip)

        # Get XML data
        l7_filter = vip_map['l7_filter']

        vip.l7_filter = l7_filter
        vip.filter_valid = False

        # If the l7_filter is a rule, set filter_valid to TRUE
        if vip_map.get('rule_id') is not None:
            vip.filter_valid = 1
            rule = Rule.objects.get(pk=vip_map.get('rule_id'))
            vip.l7_filter = '\n'.join(
                rule.rulecontent_set.all().values_list('content', flat=True))
            vip.rule = rule
        else:
            vip.filter_valid = 0
            vip.rule = None

        vip.save()

        map = dict()
        map['sucesso'] = 'sucesso'
        return self.response(dumps_networkapi(map))

    def handle_get(self, request, user, *args, **kwargs):
        """Handles a GET request to return L7 data

        URL: vip/l7/<id_vip>/
        """

        try:
            if not has_perm(user,
                            AdminPermission.VIPS_REQUEST,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            # Valid Ip ID
            if not is_valid_int_greater_zero_param(kwargs.get('id_vip')):
                self.log.error(
                    u'The id_vip parameter is not a valid value: %s.', kwargs.get('id_vip'))
                raise InvalidValueError(None, 'id_vip', kwargs.get('id_vip'))

            request_vip = RequisicaoVips.get_by_pk(kwargs.get('id_vip'))

            date = request_vip.applied_l7_datetime

            if date:
                date = date.strftime('%d/%m/%Y %H:%M:%S')

            request_vip_map = dict()
            request_vip_map['l7_filter'] = request_vip.l7_filter
            request_vip_map['rule'] = request_vip.rule
            request_vip_map['filter_applied'] = request_vip.filter_applied
            request_vip_map['rule_applied'] = request_vip.rule_applied
            request_vip_map['filter_rollback'] = request_vip.filter_rollback
            request_vip_map['rule_rollback'] = request_vip.rule_rollback
            request_vip_map['applied_l7_datetime'] = date
            request_vip_map['filter_valid'] = convert_boolean_to_int(
                request_vip.filter_valid)

            return self.response(dumps_networkapi({'vip': request_vip_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (RequisicaoVipsNotFoundError):
            return self.response_error(152)
        except (RequisicaoVipsError, GrupoError):
            return self.response_error(1)
