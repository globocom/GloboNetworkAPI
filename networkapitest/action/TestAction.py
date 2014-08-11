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


from django.shortcuts import render_to_response

from django.template import RequestContext

from networkapitest.form.TestForm import TestForm

from networkapitest.rest_test import RestClient, RestError


class TestAction(object):

    def show(self, request):
        form = TestForm()
        return render_to_response('networkapi-test.html',
                                  {'form': form, 'response_xml': ''},
                                  context_instance=RequestContext(request))

    def call_url(self, request):
        response = ''
        form = TestForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']

            auth_map = dict()
            auth_map['NETWORKAPI_USERNAME'] = form.cleaned_data['username']
            auth_map['NETWORKAPI_PASSWORD'] = form.cleaned_data['password']

            try:
                if method == 'GET':
                    status, response = RestClient().get(
                        form.cleaned_data['url'], auth_map)
                elif method == 'DELETE':
                    status, response = RestClient().delete(form.cleaned_data['url'],
                                                           form.cleaned_data[
                                                               'request_xml'],
                                                           'text/plain',
                                                           auth_map)
                elif method == 'POST':
                    status, response = RestClient().post(form.cleaned_data['url'],
                                                         form.cleaned_data[
                                                             'request_xml'],
                                                         'text/plain',
                                                         auth_map)
                elif method == 'PUT':
                    status, response = RestClient().put(form.cleaned_data['url'],
                                                        form.cleaned_data[
                                                            'request_xml'],
                                                        'text/plain',
                                                        auth_map)
            except RestError, e:
                response = e

        return render_to_response('networkapi-test.html',
                                  {'form': form, 'response_xml': response},
                                  context_instance=RequestContext(request))
