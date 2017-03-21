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
from .networkv4 import create_networkipv4
from .networkv4 import delete_networkipv4
from .networkv4 import deploy_networkipv4
from .networkv4 import get_networkipv4_by_id
from .networkv4 import get_networkipv4_by_ids
from .networkv4 import get_networkipv4_by_search
from .networkv4 import undeploy_networkipv4
from .networkv4 import update_networkipv4
from .networkv6 import create_networkipv6
from .networkv6 import delete_networkipv6
from .networkv6 import deploy_networkipv6
from .networkv6 import get_networkipv6_by_id
from .networkv6 import get_networkipv6_by_ids
from .networkv6 import get_networkipv6_by_search
from .networkv6 import undeploy_networkipv6
from .networkv6 import update_networkipv6

__all__ = (
    'get_networkipv4_by_id', 'get_networkipv4_by_ids',
    'get_networkipv4_by_search', 'create_networkipv4',
    'update_networkipv4', 'delete_networkipv4', 'undeploy_networkipv4',
    'deploy_networkipv4', 'get_networkipv6_by_id', 'get_networkipv6_by_ids',
    'get_networkipv6_by_search', 'create_networkipv6', 'update_networkipv6',
    'delete_networkipv6', 'undeploy_networkipv6', 'deploy_networkipv6')
