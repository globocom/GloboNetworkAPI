# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Brocade, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class BaseException(Exception):

    def __init__(self, **kwargs):
        super(BaseException, self).__init__(self.message % kwargs)
        self.message = self.message % kwargs


class UnsupportedFeature(BaseException):
    message = "Unsupported feature: %(msg)s"


class UnsupportedOption(BaseException):
    message = "Unsupported Value %(value)s specified for attribute %(name)s"


class ConfigError(BaseException):
    message = "Configuration error on the device: %(msg)s"


class NoValidDevice(BaseException):
    message = "No valid device found"


class StartupError(BaseException):
    message = "Device driver configuration error: %(msg)s"
