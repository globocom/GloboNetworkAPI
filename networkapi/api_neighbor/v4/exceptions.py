# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class NeighborV4NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'NeighborV4 %s do not exist.' % (msg)


class NeighborV4Error(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class NeighborV4AlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV4 already created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV4 %s already created.' % msg


class NeighborV4NotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV4 not created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV4 %s not created.' % msg


class NeighborV4DoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'NeighborV4 does not exists.'


class NeighborV6NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'NeighborV6 %s do not exist.' % (msg)


class NeighborV6Error(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class NeighborV6AlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV6 already created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV6 %s already created.' % msg


class NeighborV6NotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV6 not created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV6 %s not created.' % msg


class NeighborV6DoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'NeighborV6 does not exists.'