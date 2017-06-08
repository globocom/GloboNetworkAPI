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
from .ipv4 import create_ipv4
from .ipv4 import delete_ipv4
from .ipv4 import update_ipv4
from .ipv6 import create_ipv6
from .ipv6 import delete_ipv6
from .ipv6 import update_ipv6

__all__ = ('create_ipv4', 'update_ipv4', 'delete_ipv4', 'create_ipv6',
           'update_ipv6', 'delete_ipv6')
