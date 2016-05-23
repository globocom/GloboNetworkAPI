from rest_framework import status
from rest_framework.exceptions import APIException


class VipRequestDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Vip Request Does Not Exist.'

    def __init__(self, msg=None):
        if msg:
            self.detail = u'Vips Request %s do not exist.' % (
                msg)
        else:
            self.detail = self.default_detail


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

    def __init__(self, msg=None):
        if msg:
            self.detail = u'%s %s' % (self.default_detail, msg)
        else:
            self.detail = self.default_detail


class VipRequestAlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Vip Request already created.'

    def __init__(self, msg=None):
        self.detail = u'Vip Request <<%s>> already created.' % msg


class VipRequestNotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Vip Request not created.'

    def __init__(self, msg=None):
        self.detail = u'Vip Request <<%s>> not created.' % msg


class VipConstraintCreatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Vip request can not be deleted because it is created in equipment.'
