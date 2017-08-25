# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class VirtualInterfaceNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Virtual Interface %s do not exist.' % (msg)


class VirtualInterfaceError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VirtualInterfaceErrorV4(Exception):

    """Generic exception for everything related to Virtual Interface."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class VirtualInterfaceDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Virtual Interface does not exists.'
