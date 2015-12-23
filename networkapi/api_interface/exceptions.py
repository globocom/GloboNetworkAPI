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


class InvalidIdInterfaceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Interface ID.'

class UnsupportedEquipmentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Tryed to apply configuration on unsupported equipment interface.'

class InvalidKeyException(APIException):
	status_code = status.HTTP_400_BAD_REQUEST

	def __init__(self, key=None):
	    self.detail = u'Invalid key %s in template.' % (key)

class InterfaceTemplateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No template or multiple templates found for interface configuration.'

class InterfaceTrunkAllowedVlanException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There is no vlan range specified to configure interface in dot1q mode.'

class InterfaceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error: .'