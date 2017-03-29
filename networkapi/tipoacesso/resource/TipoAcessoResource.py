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
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_TYPE_ACCESS
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.tipoacesso.models import AccessTypeNotFoundError
from networkapi.tipoacesso.models import AccessTypeUsedByEquipmentError
from networkapi.tipoacesso.models import DuplicateProtocolError
from networkapi.tipoacesso.models import TipoAcesso
from networkapi.tipoacesso.models import TipoAcessoError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class TipoAcessoResource(RestResource):

    """Class to treat GET, POST, PUT and DELETE requests to tipo_acesso table."""

    log = logging.getLogger('TipoAcessoResource')

    def handle_get(self, request, user, *args, **kwargs):
        """GET requests to list all TipoAcesso.

        URL: /tipoacesso/
        """

        try:
            if not has_perm(user, AdminPermission.ACCESS_TYPE_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Efetua a consulta de todos os tipos de acesso
            map_list = []
            for item in TipoAcesso.objects.all():
                map_list.append(model_to_dict(item))

            # Gera response (XML) com resultados
            return self.response(dumps_networkapi({'tipo_acesso': map_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except (TipoAcessoError, GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to add new Access Type.

        URL: /tipoacesso/

        """

        try:
            if not has_perm(user, AdminPermission.ACCESS_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            xml_map, attrs_map = loads(request.raw_post_data)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag in request XML.')

            tipo_acesso_map = networkapi_map.get('tipo_acesso')
            if tipo_acesso_map is None:
                return self.response_error(3, u'There is no tipo_acesso tag in request XML.')

            # Valid protocol
            protocol = tipo_acesso_map.get('protocolo')
            if not is_valid_string_minsize(protocol, 3) or not is_valid_string_maxsize(protocol, 45) or not is_valid_regex(protocol, r'^[- a-zA-Z0-9]+$'):
                self.log.error(
                    u'Parameter protocol is invalid. Value: %s', protocol)
                raise InvalidValueError(None, 'protocol', protocol)

            access_type = TipoAcesso()
            access_type.protocolo = protocol

            try:
                TipoAcesso.objects.get(protocolo__iexact=access_type.protocolo)
                raise DuplicateProtocolError(
                    None, u'Access Type with protocol %s already exists' % protocol)
            except TipoAcesso.DoesNotExist:
                pass

            try:
                # save access type
                access_type.save()
            except Exception, e:
                self.log.error(u'Failed to save TipoAcesso.')
                raise TipoAcessoError(e, u'Failed to save TipoAcesso.')

            return self.response(dumps_networkapi({'tipo_acesso': {'id': access_type.id}}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except DuplicateProtocolError:
            return self.response_error(203, protocol)
        except (TipoAcessoError, GrupoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to edit Access Type.

        URL: /tipoacesso/<id_tipo_acesso>/

        """

        try:
            if not has_perm(user, AdminPermission.ACCESS_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Access Type ID
            tipo_acesso_id = kwargs.get('id_tipo_acesso')
            if not is_valid_int_greater_zero_param(tipo_acesso_id):
                self.log.error(
                    u'The tipo_acesso_id parameter is not a valid value: %s.', tipo_acesso_id)
                raise InvalidValueError(None, 'tipo_acesso_id', tipo_acesso_id)

            xml_map, attrs_map = loads(request.raw_post_data)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag in request XML.')

            tipo_acesso_map = networkapi_map.get('tipo_acesso')
            if tipo_acesso_map is None:
                return self.response_error(3, u'There is no tipo_acesso tag in request XML.')

            # Valid protocol
            protocol = tipo_acesso_map.get('protocolo')
            if not is_valid_string_minsize(protocol, 3) or not is_valid_string_maxsize(protocol, 45) or not is_valid_regex(protocol, r'^[- a-zA-Z0-9]+$'):
                self.log.error(
                    u'Parameter protocol is invalid. Value: %s', protocol)
                raise InvalidValueError(None, 'protocol', protocol)

            # Verify existence
            tpa = TipoAcesso.get_by_pk(tipo_acesso_id)

            tpa.protocolo = protocol

            try:
                if len(TipoAcesso.objects.filter(protocolo__iexact=protocol).exclude(id=tpa.id)) > 0:
                    raise DuplicateProtocolError(
                        None, u'Access Type with protocol %s already exists' % protocol)
            except TipoAcesso.DoesNotExist:
                pass

            with distributedlock(LOCK_TYPE_ACCESS % tipo_acesso_id):

                try:
                    # save access type
                    tpa.save()
                except Exception, e:
                    self.log.error(u'Failed to update TipoAcesso.')
                    raise TipoAcessoError(e, u'Failed to update TipoAcesso.')

            return self.response(dumps_networkapi({}))

        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except AccessTypeNotFoundError:
            return self.response_error(171, tipo_acesso_id)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except DuplicateProtocolError:
            return self.response_error(203, protocol)
        except (TipoAcessoError, GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove Access Type.

        URL: /tipoacesso/<id_tipo_acesso>/

        """

        try:
            if not has_perm(user, AdminPermission.ACCESS_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Access Type ID
            tipo_acesso_id = kwargs.get('id_tipo_acesso')
            if not is_valid_int_greater_zero_param(tipo_acesso_id):
                self.log.error(
                    u'The tipo_acesso_id parameter is not a valid value: %s.', tipo_acesso_id)
                raise InvalidValueError(None, 'tipo_acesso_id', tipo_acesso_id)

            # Verify existence
            tpa = TipoAcesso.get_by_pk(tipo_acesso_id)

            with distributedlock(LOCK_TYPE_ACCESS % tipo_acesso_id):

                # Verifica se o tipo de acesso não é utilizado por algum
                # equipamento
                if tpa.equipamentoacesso_set.count() > 0:
                    self.log.error(u'Access Type in use by equipment.')
                    raise AccessTypeUsedByEquipmentError(
                        None, u'Access Type in use by equipment.')

                tpa.delete()

            return self.response(dumps_networkapi({}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except AccessTypeNotFoundError:
            return self.response_error(171, tipo_acesso_id)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AccessTypeUsedByEquipmentError:
            return self.response_error(204, tipo_acesso_id)
        except (TipoAcessoError, GrupoError):
            return self.response_error(1)

    def get_tipo_acesso_map(self, tipo_acesso):
        tipo_acesso_map = dict()
        tipo_acesso_map['id'] = tipo_acesso.id
        tipo_acesso_map['protocolo'] = tipo_acesso.protocolo
        return tipo_acesso_map
