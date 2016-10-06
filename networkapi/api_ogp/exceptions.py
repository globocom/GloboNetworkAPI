from rest_framework import status
from rest_framework.exceptions import APIException


class ObjectGroupPermissionError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class ObjectGroupPermissionNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Object Group Permission %s do not exist.' % (msg)


class ObjectGroupPermissionGeneralError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class ObjectGroupPermissionGeneralNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Object Group Permission General %s do not exist.' % (msg)
