# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



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


class AddBlockOverrideNotDefined(CustomException):
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

class EnvironmentNotFoundError(CustomException):

    """returns exception to Environment research by primary key."""

    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)


class EnvironmentEnvironmentVipNotFoundError(CustomException):

    """returns exception to EnvironmentEnvironmentVip research by primary key."""

    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)


class EnvironmentEnvironmentVipDuplicatedError(CustomException):

    """returns exception to EnvironmentEnvironmentVip duplicated."""

    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)


class EnvironmentEnvironmentVipError(CustomException):

    """returns exception to EnvironmentEnvironmentVip error."""

    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)


class EnvironmentEnvironmentServerPoolRequestVipLinked(CustomException):

    """returns exception to EnvironmentEnvironmentVip error."""

    def __init__(self, cause, message=None):
        CustomException.__init__(self, cause, message)