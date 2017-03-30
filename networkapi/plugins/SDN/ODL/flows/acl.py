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

from json import dumps


class AclFlowBuilder(object):
    """ Class responsible for build json data for Access control list flow at
    OpenDayLight controller
    """
    def __init__(self, data):

        self.raw_data = data  # Original data
        self.flows = {}  # Processed data

    def build(self):
        pass

    def dump(self):
        if not isinstance(self.flows, dict):
            raise TypeError("self.flows must be a dictionary")

        self.build()

        return dumps(self.flows)
