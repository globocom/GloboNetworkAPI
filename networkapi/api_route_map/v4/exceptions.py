# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class RouteMapNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'RouteMap %s do not exist.' % (msg)


class RouteMapError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class RouteMapEntryNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'RouteMapEntry %s do not exist.' % (msg)


class RouteMapEntryError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class RouteMapDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'RouteMap does not exists.'

