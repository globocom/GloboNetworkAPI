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


from networkapi.interface.models import PortChannel
from networkapi.interface.models import InterfaceNotFoundError


class ChannelV3(object):
    """ Facade class that implements business rules for interfaces channels """

    def create(self, data):
        self.id = 42
        pass

    def retrieve(self, channel_name):
        """ Tries to retrieve a Port Channel based on its name """

        channel = {}
        try:
            channel = PortChannel.get_by_name(channel_name)

            # Copied from old implementation. We really need to iterate?
            for ch in channel:
                channel = model_to_dict(ch)

        except InterfaceNotFoundError as err:
            return None
        except:
            channel = model_to_dict(channel)

        return {"channel": channel}

    def update(self):
        pass

    def delete(self):
        pass

