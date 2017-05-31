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
from .networkv4 import create_networkv4
from .networkv4 import delete_networkv4
from .networkv4 import deploy_networkv4
from .networkv4 import undeploy_networkv4
from .networkv4 import update_networkv4
from .networkv6 import create_networkv6
from .networkv6 import delete_networkv6
from .networkv6 import deploy_networkv6
from .networkv6 import undeploy_networkv6
from .networkv6 import update_networkv6

__all__ = ('create_networkv4', 'update_networkv4', 'delete_networkv4',
           'deploy_networkv4', 'undeploy_networkv4', 'create_networkv6',
           'update_networkv6', 'delete_networkv6', 'deploy_networkv6',
           'undeploy_networkv6')
