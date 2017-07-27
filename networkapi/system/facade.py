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
import logging

from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.system import exceptions
from networkapi.system.models import Variable

log = logging.getLogger(__name__)


def save_variable(name, value, description):

    if not name:
        raise exceptions.InvalidIdNameException()
    if not value:
        raise exceptions.InvalidIdValueException()

    var = Variable()
    var.name = name
    var.value = value
    var.description = description

    try:
        var.save()
    except Exception, e:
        log.info("Erro inserindo variavel: %s" % (e))
        raise Exception("Erro inserindo variavel: %s" % (e))

    return var


def get_all_variables():

    variables = Variable.objects.all()

    return variables


def get_by_id(variable_id):
    try:
        var = Variable.objects.filter(id=variable_id).uniqueResult()
    except ObjectDoesNotExist:
        raise exceptions.VariableDoesNotExistException()
    return var


def get_by_name(name):
    try:
        var = Variable.objects.filter(name=name).uniqueResult()
    except ObjectDoesNotExist:
        raise exceptions.VariableDoesNotExistException()
    return var


def get_value(name, default=None):
    try:
        var = Variable.objects.filter(name=name).uniqueResult()
    except ObjectDoesNotExist:
        if default:
            return default
        raise exceptions.VariableDoesNotExistException()
    return var.value


def delete_variable(user, variable_id):
    try:
        variable = get_by_id(variable_id)
        variable.delete(user)
    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()
