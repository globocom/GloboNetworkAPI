# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

class CustomException(Exception):
    """Represents an error occurred validating a value."""
    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Cause: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')

class InvalidValueError(Exception):
    """Represents an error occurred validating a value."""
    def __init__(self, cause, param=None, value=None):
        self.cause = cause
        self.param = param
        self.value = value

class RequestVipsNotBeenCreatedError(CustomException):
    """Represents an error occurred when attempting to change a VIP that has not been created."""
    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)

class EquipmentGroupsNotAuthorizedError(CustomException):
    """Represents an error when the groups of equipment registered with the IP of the VIP request is not allowed acess."""
    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)

class EnvironmentVipError(CustomException):
    """Represents an error occurred during access to tables related to environment VIP."""
    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)

class EnvironmentVipNotFoundError(EnvironmentVipError):
    """returns exception to environment research by primary key."""
    def __init__(self, cause, message=None):
        EnvironmentVipError.__init__(self, cause, message)

class OptionVipError(CustomException):
    """Represents an error occurred during access to tables related to Option VIP."""
    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)

class OptionVipNotFoundError(OptionVipError):
    """returns exception to Option vip research by primary key."""
    def __init__(self, cause, message=None):
        OptionVipError.__init__(self, cause, message)

class OptionVipEnvironmentVipError(CustomException):
    """Represents an error occurred during access to tables related to OptionVipEnvironmentVip."""
    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)

class OptionVipEnvironmentVipNotFoundError(OptionVipEnvironmentVipError):
    """returns exception to OptionVipEnvironmentVip research by primary key."""
    def __init__(self, cause, message=None):
        OptionVipEnvironmentVipError.__init__(self, cause, message)

class OptionVipEnvironmentVipDuplicatedError(OptionVipEnvironmentVipError):
    """returns exception if OptionVip is already associated with EnvironmentVip."""
    def __init__(self, cause, message=None):
        OptionVipEnvironmentVipError.__init__(self, cause, message)


class NetworkInactiveError(CustomException):
    """Returns exception when trying to disable a network disabled"""

    def __init__(self, cause=u'Unable to remove the network because it is inactive.', message=None):
        CustomException.__init__(self, cause, message)
