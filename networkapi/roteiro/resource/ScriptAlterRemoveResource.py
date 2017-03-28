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
from networkapi.distributedlock import LOCK_SCRIPT
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
from networkapi.roteiro.models import RoteiroHasEquipamentoError
from networkapi.roteiro.models import RoteiroNameDuplicatedError
from networkapi.roteiro.models import RoteiroNotFoundError
from networkapi.roteiro.models import TipoRoteiro
from networkapi.roteiro.models import TipoRoteiroNotFoundError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class ScriptAlterRemoveResource(RestResource):

    log = logging.getLogger('ScriptAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Script.

        URL: script/<id_script>/
        """
        try:

            self.log.info('Edit Script')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_script = kwargs.get('id_script')

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
            models = script_map.get('model')
            description = script_map.get('description')

            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(
                    u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)

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

            # Find Script by ID to check if it exist
            scr = Roteiro.get_by_pk(id_script)

            # Find Script Type by ID to check if it exist
            script_type = TipoRoteiro.get_by_pk(id_script_type)

            models_old = []
            scr_models = ModeloRoteiro.objects.all().filter(roteiro__id=scr.id)
            for i in scr_models:
                models_old.append(int(i.modelo.id))

            if models is not None and type(models) is not list:
                var = int(models)
                models = []
                models.append(var)
            else:
                models = [int(x) for x in models]

            desassociar = set(models_old) - set(models)
            for i in desassociar:
                scr_model = ModeloRoteiro()
                scr_model.remover(user, int(i), int(scr.id))
            associar = set(models) - set(models_old)
            for i in associar:
                scr_models = ModeloRoteiro()
                scr_models.roteiro = scr
                scr_models.modelo = Modelo.get_by_pk(i)
                scr_models.create(user)

            # verificar se há equipamento daquele modelo que não está associado
            # a um roteiro
            for ids in models:
                equipamentos = Equipamento.objects.filter(modelo__id=int(ids))
                for equip in equipamentos:
                    try:
                        equip_roteiro = EquipamentoRoteiro.objects.filter(
                            equipamento__id=equip.id, roteiro__tipo_roteiro__id=scr.tipo_roteiro.id).uniqueResult()
                        equip_roteiro.id
                    except:
                        equip_rot = EquipamentoRoteiro()
                        equip_rot.equipamento = equip
                        equip_rot.roteiro = scr
                        equip_rot.create(user)
                        pass

            with distributedlock(LOCK_SCRIPT % id_script):

                try:
                    if not scr.roteiro.lower() == script.lower() and not scr.tipo_roteiro.id == id_script_type:
                        Roteiro.get_by_name_script(script, id_script_type)
                        raise RoteiroNameDuplicatedError(
                            None, u'Já existe um roteiro com o nome %s com tipo de roteiro %s.' % (script, script_type.tipo))
                except RoteiroNotFoundError:
                    pass

                # set variables
                scr.roteiro = script
                scr.tipo_roteiro = script_type
                scr.descricao = description

                try:
                    # update Script
                    scr.save()
                except Exception, e:
                    self.log.error(u'Failed to update the Script.')
                    raise RoteiroError(e, u'Failed to update the Script.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroNotFoundError:
            return self.response_error(165, id_script)

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except RoteiroNameDuplicatedError:
            return self.response_error(250, script, script_type.tipo)

        except RoteiroError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Script.

        URL: script/<id_script>/
        """
        try:

            self.log.info('Remove Script')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_script = kwargs.get('id_script')

            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(
                    u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)

            # Find Script by ID to check if it exist
            script = Roteiro.get_by_pk(id_script)

            with distributedlock(LOCK_SCRIPT % id_script):

                try:

                    if script.equipamentoroteiro_set.count() != 0:
                        raise RoteiroHasEquipamentoError(
                            None, u'Existe equipamento associado ao roteiro %s' % script.id)

                    # remove Script
                    script.delete()

                except RoteiroHasEquipamentoError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Script.')
                    raise RoteiroError(e, u'Failed to remove the Script.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroNotFoundError:
            return self.response_error(165, id_script)

        except RoteiroHasEquipamentoError:
            return self.response_error(197, id_script)

        except RoteiroError:
            return self.response_error(1)
