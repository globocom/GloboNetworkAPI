from rest_framework.exceptions import APIException
from rest_framework import status


class NetworkAPIException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to access the data source.'


class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation Bad Request.'

    def __init__(self, param=None):
        self.detail = u'Error validating request parameter: %s' % (param)


class ObjectDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Object Does Not Exist.'


class ScriptException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute script.'


class EnvironmentEnvironmentVipNotBoundedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There is no link between environment and environment vip.'