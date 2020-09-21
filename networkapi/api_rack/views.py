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

import glob
import logging

from django.db.transaction import commit_on_success
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_rack.permissions import Write
from networkapi.api_rack import facade, exceptions
from networkapi.api_rack.serializers import RackSerializer, DCSerializer, DCRoomSerializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.equipamento.models import Equipamento
from networkapi.system.facade import get_value as get_variable
from networkapi.system import exceptions as var_exceptions

from networkapi.distributedlock import LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT
from networkapi.api_deploy import facade as deploy_facade

log = logging.getLogger(__name__)


@permission_classes((IsAuthenticated, Write))
class RackView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("New Rack")

            if not request.DATA.get('rack'):
                raise exceptions.InvalidInputException()

            rack = facade.save_rack_dc(request.DATA.get('rack'))

            data = dict()
            rack_serializer = RackSerializer(rack)
            data['rack'] = rack_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def put(self, request, *args, **kwargs):

        try:
            log.info("PUT Rack")

            rack_id = kwargs.get("rack_id") if kwargs.get("rack_id") else None

            if not request.DATA.get('rack'):
                raise exceptions.InvalidInputException()

            rack = facade.update_rack(rack_id, request.DATA.get('rack'))

            data = dict()
            rack_serializer = RackSerializer(rack)
            data['rack'] = rack_serializer.data

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def get(self, user, *args, **kwargs):
        """Handles GET requests to list all Racks"""

        try:
            log.info('List all Racks')

            fabric_id = kwargs.get("fabric_id") if kwargs.get("fabric_id") else None
            rack_id = kwargs.get("rack_id") if kwargs.get("rack_id") else None

            if fabric_id:
                racks = facade.get_rack(fabric_id=fabric_id)
            elif rack_id:
                racks = facade.get_rack(rack_id=rack_id)
            else:
                racks = facade.get_rack()
            data = dict()
            data['racks'] = racks

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def delete(self, user, *args, **kwargs):
        """Handles DELETE requests to list all Racks
        URLs: /api/rack/<rack_id>
        """

        try:
            log.info('Delete Rack')

            rack_id = kwargs.get("rack_id")

            facade.delete_rack(rack_id)

            data = dict()

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)


class RackDeployView(APIView):

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def post(self, *args, **kwargs):
        try:
            log.info('RACK deploy.')

            rack_id = kwargs.get('rack_id')
            rack = facade.get_by_pk(rack_id)

            try:
                PATH_TO_ADD_CONFIG = get_variable('path_to_add_config')
                REL_PATH_TO_ADD_CONFIG = get_variable('rel_path_to_add_config')
            except ObjectDoesNotExist:
                raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável PATH_TO_ADD_CONFIG ou "
                                                                   "REL_PATH_TO_ADD_CONFIG.")

            path_config = PATH_TO_ADD_CONFIG + '*' + rack.nome + '*'
            arquivos = glob.glob(path_config)

            # Get all files and search for equipments of the rack
            for var in arquivos:
                filename_equipments = var.split('/')[-1]
                rel_filename = REL_PATH_TO_ADD_CONFIG + filename_equipments
                log.debug("rel_filename: %s" % rel_filename)
                # Check if file is config relative to this rack
                if rack.nome in filename_equipments:
                    # Apply config only in spines. Leaves already have all necessary config in startup
                    if "ADD" in filename_equipments:
                        # Check if equipment in under maintenance. If so, does not aplly on it
                        equipment_name = filename_equipments.split('-ADD-')[0]
                        log.debug("equipment_name: %s" % equipment_name)
                        try:
                            equip = Equipamento.get_by_name(equipment_name)
                            if not equip.maintenance:
                                lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT % (equip.id)
                                output = deploy_facade.deploy_config_in_equipment_synchronous(rel_filename, equip, lockvar)

                                log.debug("equipment output: %s" % (output))
                        except Exception as e:
                            log.exception(e)
                            raise exceptions.RackAplError(e)

            datas = dict()
            success_map = dict()

            success_map['rack_conf'] = True
            datas['sucesso'] = success_map

            return Response(datas, status=status.HTTP_201_CREATED)

        except exceptions.RackNumberNotFoundError as e:
            log.exception(e)
            raise exceptions.NetworkAPIException(e)
        except var_exceptions.VariableDoesNotExistException as e:
            log.error(e)
            raise api_exceptions.NetworkAPIException(
                'Erro buscando a variável PATH_TO_ADD_CONFIG ou REL_PATH_TO_ADD_CONFIG. Erro: %s' % e)
        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)


class RackForeman (APIView):
    def post(self, *args, **kwargs):
        try:
            log.info('RACK Foreman.')

            rack_id = kwargs.get('rack_id')
            rack = facade.get_by_pk(rack_id)
            # Create Foreman entries for rack switches
            facade.api_foreman(rack)
            raise api_exceptions.NetworkAPIException('chegou')
            return Response(datas, status=status.HTTP_201_CREATED)

        except exceptions.RackNumberNotFoundError, e:
            log.exception(e)
            raise exceptions.NetworkAPIException(e)

        except var_exceptions.VariableDoesNotExistException, e:
            log.error(e)
            raise api_exceptions.NetworkAPIException(
            'Erro ao registrar o Switch no Foreman. Erro: %s' % e)

        except Exception, e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)


class RackConfigView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("Gerando o arquivo de configuracao dos equipamentos do rack")

            rack_id = kwargs.get("rack_id")
            facade.gerar_arquivo_config([rack_id])

            data = dict()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)


class RackEnvironmentView(APIView):

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            logging.getLogger('Alocando ambientes e vlans do rack')

            rack_id = kwargs.get("rack_id")
            # facade.rack_environments_vlans(rack_id, request.user)
            facade.allocate_env_vlan(request.user, rack_id)

            data = dict()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        try:
            logging.getLogger('Remove environments and vlans.')

            rack_id = kwargs.get("rack_id")
            facade.deallocate_env_vlan(request.user, rack_id)

            data = dict()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)


class DataCenterView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("POST Datacenter")

            if not request.DATA.get('dc'):
                raise exceptions.InvalidInputException()

            dc = facade.save_dc(request.DATA.get('dc'))
            dc_serializer = DCSerializer(dc)

            data = dict()
            data['dc'] = dc_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def get(self, request, *args, **kwargs):
        try:
            log.info("GET Datacenter")

            dc = facade.listdc()

            data = dict()
            data['dc'] = dc

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def delete(self, request, *args, **kwargs):

        try:
            log.info('Delete DC')

            dc_id = kwargs.get("dc_id").split(";")

            facade.delete_dc(dc_id)

            data = dict()

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)


class FabricView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("Post - Fabric")

            if not request.DATA.get('dcrooms'):
                raise exceptions.InvalidInputException()

            dcrooms = facade.save_dcrooms(request.DATA.get('dcrooms'))

            data = dict()
            dcroom_serializer = DCRoomSerializer(dcrooms)
            data['dcroom'] = dcroom_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def put(self, request, *args, **kwargs):
        try:
            log.info("Put - Fabric")

            if not request.DATA.get('fabric'):
                raise exceptions.InvalidInputException()
            #validar o json

            fabric_id = kwargs.get('fabric_id')
            fabric = request.DATA.get('fabric')

            if fabric.get("flag"):
                fabrics = facade.update_fabric_config(fabric_id, fabric)
            else:
                fabrics = facade.edit_dcrooms(fabric_id, fabric)

            fabric_serializer = DCRoomSerializer(fabrics)
            data = dict()
            data['fabric'] = fabric_serializer.data

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def get(self, request, *args, **kwargs):
        try:
            log.info("GET Fabric")

            fabric_id = kwargs.get('fabric_id') if kwargs.get('fabric_id') else None
            fabric_name = kwargs.get('fabric_name') if kwargs.get('fabric_name') else None
            fabric_dc = kwargs.get('dc_id') if kwargs.get('dc_id') else None

            fabric = facade.get_fabric(idt=fabric_id, name=fabric_name, id_dc=fabric_dc)
            data = dict()
            data['fabric'] = fabric

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise api_exceptions.NetworkAPIException(e)

    @commit_on_success
    def delete(self, request, *args, **kwargs):

        try:
            log.info('Delete Fabric')

            fabric_id = kwargs.get("fabric_id").split(";")

            facade.delete_dcrooms(fabric_id)

            data = dict()

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            log.exception(e)
            raise api_exceptions.NetworkAPIException(e)
