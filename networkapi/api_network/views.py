# -*- coding:utf-8 -*-

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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response
from django.db.transaction import commit_on_success

import logging
from networkapi.auth import has_perm
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.admin_permission import AdminPermission

from networkapi.api_network import facade
from networkapi.api_network.permissions import Read, Write, DeployConfig
from networkapi.api_network.serializers import NetworkIPv4Serializer, NetworkIPv6Serializer
from networkapi.api_network.models import DHCPRelayIPv4, DHCPRelayIPv6
from networkapi.api_network import exceptions

from networkapi.ip.models import NetworkIPv4, NetworkIPv6, NetworkIPv4NotFoundError, NetworkIPv6NotFoundError
from networkapi.equipamento.models import Equipamento

log = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv4(request):
    '''Lists network ipv4 and filter by url parameters
    '''
    try:

        environment_vip = ''

        if request.QUERY_PARAMS.has_key("environment_vip"):
            environment_vip = str(request.QUERY_PARAMS["environment_vip"])

        networkIPv4_obj = NetworkIPv4.objects.all()

        if environment_vip:
            networkIPv4_obj = networkIPv4_obj.filter(ambient_vip__id=environment_vip)

        serializer_options = NetworkIPv4Serializer(
            networkIPv4_obj,
            many=True
        )

        return Response(serializer_options.data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()

@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv4_by_pk(request, network_id):
    '''Lists network ipv4
    '''
    try:

        networkIPv4_obj = NetworkIPv4.get_by_pk(network_id)
        dhcprelay = DHCPRelayIPv4.objects.filter(networkipv4=networkIPv4_obj)
        serializer_options = NetworkIPv4Serializer(
            networkIPv4_obj,
            many=False
        )
        serializer_options.teste(dhcprelay)

        return Response(serializer_options.data)

    except NetworkIPv4NotFoundError, exception:
        raise exceptions.InvalidNetworkIDException()
    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, Write, DeployConfig))
@commit_on_success
def networkIPv4_deploy(request, network_id):
    '''Deploy network L3 configuration in the environment routers for network ipv4

    Receives optional parameter equipments to specify what equipment should
    receive network configuration
    '''

    networkipv4 = NetworkIPv4.get_by_pk(int(network_id))
    environment = networkipv4.vlan.ambiente
    equipments_id_list = request.DATA.get("equipments", None)

    equipment_list = []
    
    if equipments_id_list is not None:
        if type(equipments_id_list) is not list:
            raise api_exceptions.ValidationException("equipments")

        for equip in equipments_id_list:
            try:
                int(equip)
            except ValueError, e:
                raise api_exceptions.ValidationException("equipments")

        #Check that equipments received as parameters are in correct vlan environment
        equipment_list = Equipamento.objects.filter(
            equipamentoambiente__ambiente = environment,
            id__in=equipments_id_list)
        log.info ("list = %s" % equipment_list)
        if len(equipment_list) != len(equipments_id_list):
            log.error("Error: equipments %s are not part of network environment." % equipments_id_list)
            raise exceptions.EquipmentIDNotInCorrectEnvException()
    else:
        #TODO GET network routers
        equipment_list = Equipamento.objects.filter(
            ipequipamento__ip__networkipv4 = networkipv4,
            equipamentoambiente__ambiente = networkipv4.vlan.ambiente,
            equipamentoambiente__is_router = 1).distinct()
        if len(equipment_list) == 0:
            raise exceptions.NoEnvironmentRoutersFoundException()

    # Check permission to configure equipments 
    for equip in equipment_list:
        # User permission
        if not has_perm(request.user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
            log.error(u'User does not have permission to perform the operation.')
            raise APIException.PermissionDenied("No permission to configure equipment %s-%s " % (equip.id, equip.nome) )

    #deploy network configuration
    if request.method == 'POST':
        returned_data = facade.deploy_networkIPv4_configuration(request.user, networkipv4, equipment_list)
    elif request.method == 'DELETE':
        returned_data = facade.remove_deploy_networkIPv4_configuration(request.user, networkipv4, equipment_list)

    return Response(returned_data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv6(request):
    '''Lists network ipv6 and filter by url parameters
    '''

    try:

        environment_vip = ''

        if request.QUERY_PARAMS.has_key("environment_vip"):
            environment_vip = str(request.QUERY_PARAMS["environment_vip"])

        networkIPv6_obj = NetworkIPv6.objects.all()

        if environment_vip:
            networkIPv6_obj = networkIPv6_obj.filter(ambient_vip__id=environment_vip)

        serializer_options = NetworkIPv6Serializer(
            networkIPv6_obj,
            many=True
        )

        return Response(serializer_options.data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()

@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def networksIPv6_by_pk(request, network_id):
    '''Lists network ipv6
    '''
    try:

        networkIPv6_obj = NetworkIPv6.get_by_pk(network_id)

        serializer_options = NetworkIPv6Serializer(
            networkIPv6_obj,
            many=False
        )

        return Response(serializer_options.data)
    except NetworkIPv6NotFoundError, exception:
        raise exceptions.InvalidNetworkIDException()
    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()

@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, Write, DeployConfig))
@commit_on_success
def networkIPv6_deploy(request, network_id):
    '''Deploy network L3 configuration in the environment routers for network ipv6

    Receives optional parameter equipments to specify what equipment should
    receive network configuration
    '''

    networkipv6 = NetworkIPv6.get_by_pk(int(network_id))
    environment = networkipv6.vlan.ambiente
    equipments_id_list = request.DATA.get("equipments", None)

    equipment_list = []
    
    if equipments_id_list is not None:
        if type(equipments_id_list) is not list:
            raise api_exceptions.ValidationException("equipments")

        for equip in equipments_id_list:
            try:
                int(equip)
            except ValueError, e:
                raise api_exceptions.ValidationException("equipments")

        #Check that equipments received as parameters are in correct vlan environment
        equipment_list = Equipamento.objects.filter(
            equipamentoambiente__ambiente = environment,
            id__in=equipments_id_list)
        log.info ("list = %s" % equipment_list)
        if len(equipment_list) != len(equipments_id_list):
            log.error("Error: equipments %s are not part of network environment." % equipments_id_list)
            raise exceptions.EquipmentIDNotInCorrectEnvException()
    else:
        #TODO GET network routers
        equipment_list = Equipamento.objects.filter(
            ipv6equipament__ip__networkipv6 = networkipv6,
            equipamentoambiente__ambiente = networkipv6.vlan.ambiente,
            equipamentoambiente__is_router = 1).distinct()
        if len(equipment_list) == 0:
            raise exceptions.NoEnvironmentRoutersFoundException()

    # Check permission to configure equipments 
    for equip in equipment_list:
        # User permission
        if not has_perm(request.user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
            log.error(u'User does not have permission to perform the operation.')
            raise APIException.PermissionDenied("No permission to configure equipment %s-%s " % (equip.id, equip.nome) )

    #deploy network configuration
    if request.method == 'POST':
        returned_data = facade.deploy_networkIPv6_configuration(request.user, networkipv6, equipment_list)
    elif request.method == 'DELETE':
        returned_data = facade.remove_deploy_networkIPv6_configuration(request.user, networkipv6, equipment_list)

    return Response(returned_data)
