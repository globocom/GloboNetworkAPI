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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_GROUP_USER
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.grupo.models import UGrupo
from networkapi.grupo.models import UGrupoNameDuplicatedError
from networkapi.grupo.models import UGrupoNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_text
from networkapi.util import is_valid_yes_no_choice


class GroupUserAlterRemoveResource(RestResource):

    log = logging.getLogger('GroupUserAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to edit Group User.

        URL: ugroup/<id_ugroup>/
        """
        try:

            self.log.info('Edit Group User')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_ugroup = kwargs.get('id_ugroup')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag of XML request.')

            ugroup_map = networkapi_map.get('user_group')
            if ugroup_map is None:
                return self.response_error(3, u'There is no value to the user_group tag of XML request.')

            id_ugroup = kwargs.get('id_ugroup')

            # Valid Group User ID
            if not is_valid_int_greater_zero_param(id_ugroup):
                self.log.error(
                    u'The id_ugroup parameter is not a valid value: %s.', id_ugroup)
                raise InvalidValueError(None, 'id_ugroup', id_ugroup)

            # Find Group User by ID to check if it exist
            ugroup = UGrupo.get_by_pk(id_ugroup)

            # Valid name
            name = ugroup_map.get('nome')
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100) or not is_valid_text(name):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            ugroup_existent = UGrupo.objects.filter(
                nome__iexact=name).exclude(id=id_ugroup)
            if len(ugroup_existent) > 0:
                raise UGrupoNameDuplicatedError(
                    None, u'User group with name %s already exists' % name)

            # Valid read
            read = ugroup_map.get('leitura')
            if not is_valid_yes_no_choice(read):
                self.log.error(u'Parameter read is invalid. Value: %s', read)
                raise InvalidValueError(None, 'read', read)

            # Valid write
            write = ugroup_map.get('escrita')
            if not is_valid_yes_no_choice(write):
                self.log.error(u'Parameter write is invalid. Value: %s', write)
                raise InvalidValueError(None, 'write', write)

            # Valid edit
            edit = ugroup_map.get('edicao')
            if not is_valid_yes_no_choice(edit):
                self.log.error(u'Parameter edit is invalid. Value: %s', edit)
                raise InvalidValueError(None, 'edit', edit)

            # Valid remove
            remove = ugroup_map.get('exclusao')
            if not is_valid_yes_no_choice(remove):
                self.log.error(
                    u'Parameter remove is invalid. Value: %s', remove)
                raise InvalidValueError(None, 'remove', remove)

            ugroup.nome = name
            ugroup.leitura = read
            ugroup.escrita = write
            ugroup.edicao = edit
            ugroup.exclusao = remove

            with distributedlock(LOCK_GROUP_USER % id_ugroup):
                try:
                    # save user group
                    ugroup.save()
                except Exception, e:
                    self.log.error(u'Failed to save the GroupUser.')
                    raise GrupoError(e, u'Failed to save the GroupUser.')

                return self.response(dumps_networkapi({'user_group': {'id': ugroup.id}}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except UGrupoNameDuplicatedError:
            return self.response_error(182, name)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except UGrupoNotFoundError:
            return self.response_error(180, id_ugroup)
        except GrupoError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove Group User.

        URL: ugroup/<id_ugroup>/
        """
        try:

            self.log.info('Remove Group User')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_ugroup = kwargs.get('id_ugroup')

            # Valid Group User ID
            if not is_valid_int_greater_zero_param(id_ugroup):
                self.log.error(
                    u'The id_ugroup parameter is not a valid value: %s.', id_ugroup)
                raise InvalidValueError(None, 'id_ugroup', id_ugroup)

            # Find Group User by ID to check if it exist
            ugroup = UGrupo.get_by_pk(id_ugroup)

            with distributedlock(LOCK_GROUP_USER % id_ugroup):

                ugroup.delete()
                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UGrupoNotFoundError:
            return self.response_error(180, id_ugroup)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except GrupoError:
            return self.response_error(1)
