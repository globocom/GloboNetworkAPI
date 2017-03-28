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
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_ENVIRONMENT_VIP
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv6
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentVipResource(RestResource):

    """Class that receives requests related to the table 'EnvironmentVip'."""

    log = logging.getLogger('EnvironmentVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests list all Environment VIP.

        URL: environmentvip/all/
        """

        try:

            self.log.info('List all Environment VIP')

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Rules

            evips = EnvironmentVip.objects.all()

            evip_list = []

            for evip in evips:
                evip_list.append(model_to_dict(evip))

            return self.response(dumps_networkapi({'environment_vip': evip_list}))

        except (EnvironmentVipError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
        except BaseException, e:
            self.log.error(e)
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to insert Environment VIP.

        URL: environmentvip/
        """

        try:

            self.log.info('Add Environment VIP')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            environmentvip_map = networkapi_map.get('environment_vip')
            if environmentvip_map is None:
                return self.response_error(3, u'There is no value to the environment_vip tag of XML request.')

            # New Environment Vip
            environment_vip = EnvironmentVip()

            # Valid Environment Vip
            environment_vip.valid_environment_vip(environmentvip_map)

            try:
                # Save Environment Vip
                environment_vip.save()
            except Exception, e:
                self.log.error(u'Failed to save the environment vip.')
                raise EnvironmentVipError(
                    e, u'Failed to save the environment vip')

            environment_map = dict()
            environment_map['id'] = environment_vip.id

            return self.response(dumps_networkapi({'environment_vip': environment_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except EnvironmentVipError:
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to change Environment VIP.

        URL: environmentvip/<id_environment_vip>/
        """

        try:

            self.log.info('Change Environment VIP')

            id_environment_vip = kwargs.get('id_environment_vip')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            environmentvip_map = networkapi_map.get('environment_vip')
            if environmentvip_map is None:
                return self.response_error(3, u'There is no value to the environment_vip tag of XML request.')

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(id_environment_vip):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', id_environment_vip)
                raise InvalidValueError(
                    None, 'id_environment_vip', id_environment_vip)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(id_environment_vip)

            with distributedlock(LOCK_ENVIRONMENT_VIP % id_environment_vip):

                # Valid Environment Vip
                environment_vip.valid_environment_vip(environmentvip_map)

                try:
                    # Update Environment Vip
                    environment_vip.save()
                except Exception, e:
                    self.log.error(u'Failed to update the environment vip.')
                    raise EnvironmentVipError(
                        e, u'Failed to update the environment vip')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except EnvironmentVipError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests PUT to delete Environment VIP.

        URL: environmentvip/<id_environment_vip>/
        """

        try:

            self.log.info('Delete Environment VIP')

            id_environment_vip = kwargs.get('id_environment_vip')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(id_environment_vip):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', id_environment_vip)
                raise InvalidValueError(
                    None, 'id_environment_vip', id_environment_vip)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(id_environment_vip)

            with distributedlock(LOCK_ENVIRONMENT_VIP % id_environment_vip):

                # Find networkIPv4 by Environment VIP to check if is greater
                # than zero
                if len(NetworkIPv4.objects.filter(ambient_vip=environment_vip.id)) > 0:
                    return self.response_error(284)

                # Find networkIPv6 by Environment VIP to check if is greater
                # than zero
                if len(NetworkIPv6.objects.filter(ambient_vip=environment_vip.id)) > 0:
                    return self.response_error(285)

                try:
                    # Delete Environment Vip
                    environment_vip.delete()
                except Exception, e:
                    self.log.error(u'Failed to delete the environment vip.')
                    raise EnvironmentVipError(
                        e, u'Failed to delete the environment vip')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except EnvironmentVipError:
            return self.response_error(1)
