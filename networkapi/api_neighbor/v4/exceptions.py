# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class NeighborNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Neighbor %s do not exist.' % (msg)


class NeighborError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class NeighborErrorV4(Exception):

    """Generic exception for everything related to Neighbor."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class NeighborDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Neighbor does not exists.'


class NeighborAlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Neighbor already created.'

    def __init__(self, msg=None):
        self.detail = u'Neighbor %s already created.' % msg


class NeighborNotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Neighbor not created.'

    def __init__(self, msg=None):
        self.detail = u'Neighbor %s not created.' % msg