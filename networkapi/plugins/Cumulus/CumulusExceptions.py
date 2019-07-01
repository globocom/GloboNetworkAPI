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

class MaxRetryAchieved(Exception):
    """Exceeded the max retry times to connect to the server"""
    pass

class MaxTimeWaitExceeded(Exception):
    """Exceeded the max time for waiting the pending be resolved"""
    pass

class ConfigurationError(Exception):
    """Raise this expection every time that cumulus cli displays an error message when applying configurations"""
    pass

class ConfigurationWarning(Exception):
    """Raise this expection when cumulus shows an warning message in staging"""
    pass