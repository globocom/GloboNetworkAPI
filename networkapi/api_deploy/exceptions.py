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

from rest_framework.exceptions import APIException
from rest_framework import status


class ConnectionException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed trying to connect to equipment.'

class InvalidFilenameException(APIException):
	status_code = status.HTTP_400_BAD_REQUEST

	def __init__(self, filename=None):
	    self.default_detail = u'Invalid filename: ' % (filename)

class InvalidEquipmentAccessException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No access or multiple accesses found for equipment.'

class LoadEquipmentModuleException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, module_name=None):
	    self.default_detail = u'Could not load equipment module: ' % (module_name)

class UnsupportedEquipmentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Tryed to apply configuration on unsupported equipment interface.'

