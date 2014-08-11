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


from django.forms import *


class TestForm(Form):

    url = URLField(widget=widgets.Textarea(
        {'cols': '100', 'rows': '1'}), label=u'URL', initial='http://', required=True)
    #method = CharField(max_length=6, label=u'Método', required=True)
    method = ChoiceField(choices=[('DELETE', 'DELETE'), ('GET', 'GET'),
                                  ('POST', 'POST'), ('PUT', 'PUT')], label=u'Método', required=True)
    username = CharField(
        max_length=45, label=u'Usuário', initial='ORQUESTRACAO', required=True)
    password = CharField(max_length=45, label=u'Senha',
                         initial='93522a36bf2a18e0cc25857e06bbfe8b', required=True)
    request_xml = CharField(widget=widgets.Textarea(
        {'cols': '100', 'rows': '20'}), label=u'XML Requisição', required=False)
