# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class AllEquipmentsAreInMaintenanceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'All equipments to be configured are in maintenance mode.'

    def __init__(self, param=default_detail, equips=None):
        self.detail = param if not equips else "{} Equipments: {}".format(param, equips)


class EquipmentInvalidValueException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Value.'

    def __init__(self, param=default_detail):
        self.detail = param


class UserDoesNotHavePermInAllEqptException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'User does not have permission to update conf in eqpt. \
                Verify the permissions of user group with equipment group'

    def __init__(self, param=default_detail):
        self.detail = param
