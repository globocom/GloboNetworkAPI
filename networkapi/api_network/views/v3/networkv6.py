# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_equipment import permissions as perm_eqpt
from networkapi.api_network import permissions
from networkapi.api_network import tasks
from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.serializers import v3 as serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class NetworkIPv6View(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of networkv6 by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_networkipv6_by_search(self.search)
            networks = obj_model['query_set']
            only_main_property = False
        else:
            obj_ids = kwargs.get('obj_ids').split(';')
            networks = facade.get_networkipv6_by_ids(obj_ids)
            only_main_property = True
            obj_model = None

        # serializer networks
        serializer_net = serializers.NetworkIPv6V3Serializer(
            networks,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_net,
            main_property='networks',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('networkv6_post')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_objv6_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Creates list of networkv6."""

        data = request.DATA

        json_validate(SPECS.get('networkv6_post')).validate(data)

        response = list()
        for networkv6 in data['networks']:
            vl = facade.create_networkipv6(networkv6, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('networkv6_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_objv6_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Updates list of networkv6."""

        data = request.DATA

        json_validate(SPECS.get('networkv6_put')).validate(data)

        response = list()
        for networkv6 in data['networks']:
            vl = facade.update_networkipv6(networkv6, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_objv6_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Deletes list of networkv6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_networkipv6(obj_ids, request.user)

        return Response(response, status=status.HTTP_200_OK)


class Networkv6AsyncView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('ipv6_post')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_objv6_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create NetworkV6."""

        response = list()
        nets = request.DATA
        json_validate(SPECS.get('networkv6_post')).validate(nets)

        user = request.user

        for net in nets['networks']:
            task_obj = tasks.create_networkv6.apply_async(args=[net, user.id],
                                                          queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('ipv6_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_objv6_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Edit NetworkV6."""

        response = list()
        nets = request.DATA
        json_validate(SPECS.get('networkv6_put')).validate(nets)

        user = request.user

        for net in nets['networks']:
            task_obj = tasks.update_networkv6.apply_async(args=[net, user.id],
                                                          queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_objv6_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete NetworkV6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')

        user = request.user

        for obj_id in obj_ids:
            task_obj = tasks.delete_networkv6.apply_async(
                args=[obj_id, user.id], queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)


class NetworkIPv6DeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 perm_eqpt.Write))
    @permission_obj_apiview([permissions.deploy_objv6_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Deploy NetworkV6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            # deploy network configuration
            status_deploy = facade.deploy_networkipv6(obj_id, request.user)
            response.append({
                'status': status_deploy,
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 perm_eqpt.Write))
    @permission_obj_apiview([permissions.deploy_objv6_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Undeploy NetworkV6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            # deploy network configuration
            status_deploy = facade.undeploy_networkipv6(obj_id, request.user)
            response.append({
                'status': status_deploy,
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)


class Networkv6DeployAsyncView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 perm_eqpt.Write))
    @permission_obj_apiview([permissions.deploy_objv6_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Deploy NetworkV6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')

        user = request.user.id

        for obj_id in obj_ids:
            task_obj = tasks.deploy_networkv6.apply_async(
                args=[obj_id, user.id], queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 perm_eqpt.Write))
    @permission_obj_apiview([permissions.deploy_objv6_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Undeploy NetworkV6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')

        user = request.user.id

        for obj_id in obj_ids:
            task_obj = tasks.undeploy_networkv6.apply_async(
                args=[obj_id, user.id], queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)


class NetworkIPv6ForceView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('networkv6_post')
    @permission_classes_apiview((IsAuthenticated, permissions.WriteForce))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Creates list of networkv6."""

        data = request.DATA

        json_validate(SPECS.get('networkv6_post')).validate(data)

        response = list()
        for networkv6 in data['networks']:
            vl = facade.create_networkipv6(networkv6, request.user,
                                           force=True)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('networkv6_put')
    @permission_classes_apiview((IsAuthenticated, permissions.WriteForce))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Updates list of networkv6."""

        data = request.DATA

        json_validate(SPECS.get('networkv6_put')).validate(data)

        response = list()
        for networkv6 in data['networks']:
            vl = facade.update_networkipv6(networkv6, request.user,
                                           force=True)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.WriteForce))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Deletes list of networkv6."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_networkipv6(obj_ids, request.user,
                                  force=True)

        return Response(response, status=status.HTTP_200_OK)
