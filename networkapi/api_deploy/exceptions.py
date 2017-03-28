# -*- coding: utf-8 -*-
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
from rest_framework import status
from rest_framework.exceptions import APIException


class CommandErrorException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: Error applying command on equipment. Equipment returned error status.'

    def __init__(self, msg=None):
        self.detail = u'Error: Error applying command on equipment. Equipment returned error status. <<%s>>' % (
            msg)


class ConnectionException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed trying to connect to equipment.'


class InvalidCommandException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: Invalid command sent to equipment. Please check template syntax or module used.'

    def __init__(self, msg=None):
        self.detail = u'Error: Invalid command sent to equipment: << %s >>' % (
            msg)


class InvalidEquipmentAccessException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No access or multiple accesses found for equipment.'


class InvalidFilenameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid filename.'

    def __init__(self, filename=None):
        self.detail = u'Invalid filename: %s' % (filename)


class InvalidKeyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Request has no expected key(s).'

    def __init__(self, key_name=None):
        self.detail = u'Expected key not present in request: %s' % (key_name)


class LoadEquipmentModuleException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = u'Could not load equipment module: '

    def __init__(self, module_name=None):
        self.detail = u'Could not load equipment module: ' % (module_name)


class UnableToVerifyResponse(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: Could not match equipment response in any known behavior. Please check config for status.'


class UnsupportedEquipmentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Tryed to apply configuration on unsupported equipment interface.'
