# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class EquipmentWithoutAccessException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipment has no access.'

    def __init__(self, name=None):
        self.detail = u'Equipment %s has no access.' % name if name \
            else self.default_detail


class PortChannelNotSupportedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Getting port-channel is not supported by equipment ' \
        'plugin.'

    def __init__(self, name=None):
        self.detail = u'Getting port-channel is not supported by plugin ' \
            u'of equipment %s.' % name if name else self.default_detail
