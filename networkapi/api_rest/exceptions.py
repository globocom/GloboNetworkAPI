from rest_framework import status
from rest_framework.exceptions import APIException


class NetworkAPIException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to access the data source.'

    def __init__(self, detail=None):
        detail = detail if detail else self.default_detail
        self.detail = u'%s' % (detail)


class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation Bad Request.'

    def __init__(self, param=None):
        self.detail = u'Error validating request parameter: %s' % (param)


class ValidationExceptionJson(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, param=None):
        self.detail = param


class ObjectDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Object Does Not Exist.'

    def __init__(self, detail=None):
        detail = detail if detail else self.default_detail
        self.detail = u'%s' % (detail)


class ScriptException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute script.'


class EnvironmentEnvironmentVipNotBoundedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There is no link between environment and environment vip.'
