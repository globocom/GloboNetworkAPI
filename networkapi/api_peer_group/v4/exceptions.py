# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class PeerGroupNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'PeerGroup %s do not exist.' % (msg)


class PeerGroupError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class EnvironmentPeerGroupNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'EnvironmentPeerGroup %s do not exist.' % (msg)


class EnvironmentPeerGroupError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg

