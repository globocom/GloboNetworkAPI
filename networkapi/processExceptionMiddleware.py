import re

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


class LoggingMiddleware(object):

    def process_exception(self, request, exception):
        """ HIDE PASSWORD VALUES"""

        # Get POST value
        msg = ''
        post_values = request.POST.copy()
        for values in post_values:
            r = re.compile('<password>(.*?)</password>')
            m = r.search(post_values[values])
            if m:
                password = m.group(1)
                msg = re.sub(password, "****", post_values[values])

            post_values[values] = msg

        request.POST = post_values

        if(post_values.has_key('password')):

            # Change PASSWORD value to '*'
            post_values['password'] = '****'
            request.POST = post_values

        # Get META value
        meta_values = request.META.copy()

        if(meta_values.has_key('HTTP_NETWORKAPI_PASSWORD')):

            # Change HTTP_NETWORKAPI_PASSWORD value to '*'
            meta_values['HTTP_NETWORKAPI_PASSWORD'] = '****'
            request.META = meta_values
