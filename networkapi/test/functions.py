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


from networkapi.test import xml2dict
import re
import httplib
import string
import random


def string_generator(size=6, chars=string.ascii_letters):
    """Generator string based on the parameters passed.

    @param size: Size limit of string. Default: 6
    @param chars: string.ascii_letters Default: 200 - Use the constant string class
    """
    return ''.join(random.choice(chars) for x in range(size))


class CodeError():

    INVALID_VALUE_ERROR = 269


def valid_response(response, status_code=httplib.OK):
    """Validates if the response is valid depending on the Http Status code past.

    @param response:  Http Response
    @param status_code: Http Status Code - Default: 200
    """
    assert response.status_code == status_code


def valid_content(response, key=None, force_list=False):
    """Validates if the response is valid

    @param response:  Http Response
    @param key:  content Key. Default: None

    @return: Content Response
    """
    content = xml2dict(response.content)
    assert content != None
    assert content != ""

    if key is not None:

        if key in content:
            if force_list and (type(content[key]) == dict or type(content[key]) == str or type(content[key]) == unicode):
                return [content.get(key)]
            else:
                return content.get(key)
        else:
            assert content.get(key) != None

    return content


def valid_get_all(content, obj):
    """

    @param content: Http content
    @param obj: Object type
    """
    assert len(content) == len(obj.objects.all())


def valid_get_filtered(content, obj, query):
    """

    @param content: Http content
    @param obj: Object type
    @param query: Query to filter
    """
    if query is not None:
        qs = obj.objects.filter(query)
    else:
        qs = obj.objects.all()

    assert len(content) == len(qs)


def is_valid_attr(dicts, key, minsize=None, maxsize=None, regex=None, instance=None, required=True):
    """Valida o atributo passado

    @todo:  arrumar doc

    @param dicts: Dicionario de dados.
    @param key: key do atributo
    @param minsize: Min size of the value to be validated.
    @param maxsize: Max size of the value to be validated.
    @param regex: Regex of the value be validated.
    @param instance: type instance of the value be validated. 
    @param required: Check if the value can be None.
    """

    if required == True:

        assert key in dicts

        if key in dicts:

            if minsize is not None:

                assert len(dicts[key]) > minsize

            if maxsize is not None:

                assert maxsize < len(dicts[key])

            if regex is not None:

                pattern = re.compile(regex)
                assert pattern.match(dicts[key])

            if instance is not None:
                assert isinstance(dicts[key], instance)
