# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class AsnNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'ASN %s do not exist.' % (msg)


class AsnError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class AsnAssociatedToEquipmentError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'AS is associated with at least one Equipment.'

    def __init__(self, msg=None):
        if msg:
            self.detail = msg
        else:
            self.detail = self.default_detail


class AsnErrorV4(Exception):

    """Generic exception for everything related to AS."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class AsnDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'AS doesn not exists.'


class AsnEquipmentNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'ASN %s do not exist.' % (msg)


class AsnEquipmentError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg
