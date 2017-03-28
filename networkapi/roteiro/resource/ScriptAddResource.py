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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.equipamento.models import Modelo
from networkapi.equipamento.models import ModeloRoteiro
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.roteiro.models import Roteiro
from networkapi.roteiro.models import RoteiroError
from networkapi.roteiro.models import RoteiroNameDuplicatedError
from networkapi.roteiro.models import RoteiroNotFoundError
from networkapi.roteiro.models import TipoRoteiro
from networkapi.roteiro.models import TipoRoteiroNotFoundError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class ScriptAddResource(RestResource):

    log = logging.getLogger('ScriptAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Script.

        URL: script/
        """

        try:

            self.log.info('Add Script')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            script_map = networkapi_map.get('script')
            if script_map is None:
                return self.response_error(3, u'There is no value to the script tag  of XML request.')

            # Get XML data
            script = script_map.get('script')
            id_script_type = script_map.get('id_script_type')
            model = script_map.get('model')
            description = script_map.get('description')

            # Valid Script
            if not is_valid_string_minsize(script, 3) or not is_valid_string_maxsize(script, 40):
                self.log.error(
                    u'Parameter script is invalid. Value: %s', script)
                raise InvalidValueError(None, 'script', script)

            # Valid ID Script Type
            if not is_valid_int_greater_zero_param(id_script_type):
                self.log.error(
                    u'The id_script_type parameter is not a valid value: %s.', id_script_type)
                raise InvalidValueError(None, 'id_script_type', id_script_type)

            # Valid description
            if not is_valid_string_minsize(description, 3) or not is_valid_string_maxsize(description, 100):
                self.log.error(
                    u'Parameter description is invalid. Value: %s', description)
                raise InvalidValueError(None, 'description', description)

            # Find Script Type by ID to check if it exist
            script_type = TipoRoteiro.get_by_pk(id_script_type)

            try:
                Roteiro.get_by_name_script(script, id_script_type)
                raise RoteiroNameDuplicatedError(None, u'Já existe um roteiro com o nome %s com tipo de roteiro %s.'
                                                 % (script, script_type.tipo))
            except RoteiroNotFoundError:
                pass

            scr = Roteiro()

            # set variables
            scr.roteiro = script
            scr.tipo_roteiro = script_type
            scr.descricao = description

            modelo_list = []

            try:
                # save Script
                scr.save()
            except Exception, e:
                self.log.error(u'Failed to save the Script.')
                raise RoteiroError(e, u'Failed to save the Script.')

            # associar o modelo ao roteiro
            try:
                if type(model) is unicode:
                    item = model
                    model = []
                    model.append(item)
                for ids in model:
                    modelos = ModeloRoteiro()
                    modelos.roteiro = scr
                    modelo = Modelo().get_by_pk(int(ids))
                    modelos.modelo = modelo
                    modelos.create(user)
                    modelo_list.append(modelos.modelo)
            except Exception, e:
                raise RoteiroError(e, u'Failed to save modelo_roteiro.')

            # verificar se há equipamento daquele modelo que não está associado
            # a um roteiro
            for ids in modelo_list:
                equipamentos = Equipamento.objects.filter(modelo__id=ids.id)
                for equip in equipamentos:
                    equip_roteiro = EquipamentoRoteiro.objects.filter(
                        equipamento=equip.id)
                    for rot in equip_roteiro:
                        if not rot.roteiro.tipo_roteiro == scr.tipo_roteiro:
                            try:
                                equip_roteiro = EquipamentoRoteiro()
                                equip_roteiro.equipamento = equip
                                equip_roteiro.roteiro = scr
                                equip_roteiro.create(user)
                            except:
                                pass

            script_map = dict()
            script_map['script'] = model_to_dict(
                scr, exclude=['roteiro', 'tipo_roteiro', 'descricao'])

            return self.response(dumps_networkapi(script_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except RoteiroNameDuplicatedError:
            return self.response_error(250, script, script_type.tipo)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroError:
            return self.response_error(1)
