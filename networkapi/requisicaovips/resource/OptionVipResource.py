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

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_OPTIONS_VIP
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipError
from networkapi.exception import OptionVipNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.requisicaovips.models import OptionVip
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class OptionVipResource(RestResource):

    """Class that receives requests related to the table 'OptionVip'."""

    log = logging.getLogger('OptionVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to insert Option VIP.

        URL: optionvip/
        """

        try:

            self.log.info('Add Option VIP')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            optionvip_map = networkapi_map.get('option_vip')
            if optionvip_map is None:
                return self.response_error(3, u'There is no value to the option_vip tag  of XML request.')

            # New Option Vip
            option_vip = OptionVip()

            # Valid Option Vip
            option_vip.valid_option_vip(optionvip_map)

            try:
                # Save Option Vip
                option_vip.save()
            except Exception, e:
                self.log.error(u'Failed to save the option vip.')
                raise OptionVipError(e, u'Failed to save the option vip')

            option_map = dict()
            option_map['option_vip'] = model_to_dict(option_vip, fields=['id'])

            return self.response(dumps_networkapi(option_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except OptionVipError:
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to change Option VIP.

        URL: optionvip/<id_option_vip>/
        """

        try:

            self.log.info('Change Option VIP')

            id_option_vip = kwargs.get('id_option_vip')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            optionvip_map = networkapi_map.get('option_vip')
            if optionvip_map is None:
                return self.response_error(3, u'There is no value to the option_vip tag  of XML request.')

            # Valid Option VIP ID
            if not is_valid_int_greater_zero_param(id_option_vip):
                self.log.error(
                    u'The id_option_vip parameter is not a valid value: %s.', id_option_vip)
                raise InvalidValueError(None, 'id_option_vip', id_option_vip)

            # Find Option VIP by ID to check if it exist
            option_vip = OptionVip.get_by_pk(id_option_vip)

            with distributedlock(LOCK_OPTIONS_VIP % id_option_vip):

                # Valid Option Vip
                option_vip.valid_option_vip(optionvip_map)

                try:
                    # Update Option Vip
                    option_vip.save()
                except Exception, e:
                    self.log.error(u'Failed to update the option vip.')
                    raise OptionVipError(e, u'Failed to update the option vip')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except OptionVipNotFoundError:
            return self.response_error(289)

        except OptionVipError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests PUT to delete Option VIP.

        URL: optionvip/<id_option_vip>/
        """

        try:

            self.log.info('Delete Option VIP')

            id_option_vip = kwargs.get('id_option_vip')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Option VIP ID
            if not is_valid_int_greater_zero_param(id_option_vip):
                self.log.error(
                    u'The id_option_vip parameter is not a valid value: %s.', id_option_vip)
                raise InvalidValueError(None, 'id_option_vip', id_option_vip)

            # Find Option VIP by ID to check if it exist
            option_vip = OptionVip.get_by_pk(id_option_vip)

            with distributedlock(LOCK_OPTIONS_VIP % id_option_vip):

                try:
                    # Delete Option Vip
                    option_vip.delete(user)
                except Exception, e:
                    self.log.error(u'Failed to delete the option vip.')
                    raise OptionVipError(e, u'Failed to delete the option vip')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except OptionVipNotFoundError:
            return self.response_error(289)

        except OptionVipError:
            return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get Option VIP.

        URL: optionvip/<id_option_vip>/
        """

        try:

            self.log.info('Get Option VIP by ID')

            id_option_vip = kwargs.get('id_option_vip')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Option VIP ID
            if not is_valid_int_greater_zero_param(id_option_vip):
                self.log.error(
                    u'The id_option_vip parameter is not a valid value: %s.', id_option_vip)
                raise InvalidValueError(None, 'id_option_vip', id_option_vip)

            try:

                # Find Option VIP by ID to check if it exist
                option_vip = OptionVip.objects.get(id=id_option_vip)

            except ObjectDoesNotExist, e:
                self.log.error(
                    u'There is no option vip with pk = %s.', id_option_vip)
                return self.response_error(289)

            option_map = dict()
            option_map['option_vip'] = model_to_dict(option_vip)

            return self.response(dumps_networkapi(option_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except OptionVipNotFoundError:
            return self.response_error(289)

        except OptionVipError:
            return self.response_error(1)
