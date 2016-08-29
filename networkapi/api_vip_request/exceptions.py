# -*- coding:utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class VipRequestNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request %s do not exist.' % (msg)


class VipRequestError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VipRequestPortNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request Port %s do not exist.' % (msg)


class VipRequestPortError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VipRequestPortOptionVipNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request Port Option Vip %s do not exist.' % (msg)


class VipRequestPortOptionVipError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VipRequestPortPoolNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request Port Pool %s do not exist.' % (msg)


class VipRequestPortPoolError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VipRequestOptionVipNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request Port Option Vip %s do not exist.' % (msg)


class VipRequestOptionVipError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VipRequestDSCPNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request Dscp %s do not exist.' % (msg)


class VipRequestDSCPError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class VipRequestGroupPermissionNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'Vips Request Group Permission %s do not exist.' % (msg)


class VipRequestGroupPermissionError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


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
    default_detail = 'Vip with ipv4 or ipv6 already exists.'


class CreatedVipRequestValuesException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Vip Request already created. Cannot change values.'

    def __init__(self, msg=None):
        self.detail = u'Not is possible to change some values in vip request when is created. Values prohibited:<<%s>>' % (
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

    def __init__(self, msg=None):
        if msg:
            self.detail = u'Vip request %s can not be deleted because it is created in equipment' % msg
        else:
            self.detail = self.default_detail
