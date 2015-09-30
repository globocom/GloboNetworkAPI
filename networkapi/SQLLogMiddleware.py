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


import logging


class SQLLogMiddleware(object):

    log = logging.getLogger('SQLLogMiddleware')

    """Loga os SQLs executados em uma requisição."""

    def process_response(self, request, response):
        from django.db import connection
        for q in connection.queries:
            self.log.debug(
                u'Consulta: %s, Tempo gasto: %s', q['sql'], q['time'])
        return response
