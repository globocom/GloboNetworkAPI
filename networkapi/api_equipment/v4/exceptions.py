# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidConfigurationFormatException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid configuration format.'

    def __init__(self, config_format=None, formats=None):
        self.detail = u'Invalid configuration format: %s. Valid formats ' \
            u'are: %s.' % (config_format, ', '.join(formats or ())) \
            if config_format else self.default_detail


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
