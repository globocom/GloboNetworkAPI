from rest_framework import status
from rest_framework.exceptions import APIException


class VipRequestDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Vip Request Does Not Exist.'


class EnvironmentVipDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Environment Vip Does Not Exist.'


class InvalidIdVipRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Vip Request.'


class AlreadyVipRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Vip with ip or ipv4 already exists.'


class CreatedVipRequestValuesException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Vip Request already created. Cannot change values.'

    def __init__(self, msg=None):
        self.detail = u'Not is possible to change vip request when is created. <<%s>>' % (
            msg)


class ServerPoolMemberDiffEnvironmentVipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Server Pool Member is associated with different environment vip of vip request.'

    def __init__(self, msg=None):
        self.detail = u'Server Pool Member is associated with different environment vip of vip request. <<%s>>' % (
            msg)


class IpNotFoundByEnvironment(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'IP environment is different of environment vip request'
