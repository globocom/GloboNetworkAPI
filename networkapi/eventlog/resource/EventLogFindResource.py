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
from datetime import datetime

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.eventlog.models import EventLog
from networkapi.eventlog.models import EventLogError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.settings import API_VERSION
from networkapi.util import cache_function
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_minsize


def get_logs(eventlog):
    """
        Joins all data needed
    """
    itens = []
    for log in eventlog:
        log_dict = prepares_logs(log)
        itens.append(log_dict)

    return itens


def prepares_logs(log):
    log_dict = dict()
    log_dict = model_to_dict(log)
    log_dict['nome_usuario'] = log.usuario.nome
    log_dict['hora_evento'] = log_dict[
        'hora_evento'].strftime('%d/%m/%Y %H:%M')

    return log_dict


class EventLogFindResource(RestResource):
    log = logging.getLogger('EventLogFindResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to find all logs by search parameters.

        URLs: /eventlog/find/
        """

        self.log.info('find all logs')

        try:
            # Common validations

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(
                    'User does not have permission to perform this operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(
                request.raw_post_data, ['searchable_columns', 'asorting_cols'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            eventlog_map = networkapi_map.get('eventlog')
            if eventlog_map is None:
                msg = u'There is no value to the eventlog tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            start_record = eventlog_map.get('start_record')
            end_record = eventlog_map.get('end_record')
            asorting_cols = eventlog_map.get('asorting_cols')
            searchable_columns = eventlog_map.get('searchable_columns')
            custom_search = eventlog_map.get('custom_search')

            usuario = eventlog_map.get('usuario')
            data_inicial = eventlog_map.get('data_inicial')
            hora_inicial = eventlog_map.get('hora_inicial')
            data_final = eventlog_map.get('data_final')
            hora_final = eventlog_map.get('hora_final')
            acao = eventlog_map.get('acao')
            funcionalidade = eventlog_map.get('funcionalidade')
            parametro = eventlog_map.get('parametro')

            # Start with all

            eventlog = EventLog.objects.all()
            eventlog = eventlog.order_by('-id')

            if usuario != '0':
                eventlog = eventlog.filter(usuario=usuario)

            if acao is not None:
                eventlog = eventlog.filter(acao=acao)

            if funcionalidade != '0':
                eventlog = eventlog.filter(funcionalidade=funcionalidade)

            if data_inicial is not None:
                if data_final is not None:
                    # Concatenate strings
                    data_inicial = data_inicial + ' ' + hora_inicial + ':00'
                    data_final = data_final + ' ' + hora_final + ':59'

                    # Parse to datetime format
                    data_inicial = datetime.strptime(
                        data_inicial, '%d/%m/%Y %H:%M:%S')
                    data_final = datetime.strptime(
                        data_final, '%d/%m/%Y %H:%M:%S')

                    eventlog = eventlog.filter(
                        hora_evento__gte=data_inicial, hora_evento__lte=data_final)
            else:
                # Concatenate strings
                hora_inicial = hora_inicial + ':00'
                hora_final = hora_final + ':59'

                # Filter by time, ignoring the date
                eventlog = eventlog.extra(
                    where=["time(hora_evento) >= '" + hora_inicial + "' and time(hora_evento) <= '" + hora_final + "'"])

            if parametro is not None:
                eventlog = eventlog.filter(parametro_atual__contains=parametro) | eventlog.filter(
                    parametro_anterior__contains=parametro)
                pass

            eventlog, total = build_query_to_datatable(
                eventlog, asorting_cols, custom_search, searchable_columns, start_record, end_record)

            itens = get_logs(eventlog)

            eventlog_map = dict()
            eventlog_map['eventlog'] = itens
            eventlog_map['total'] = total

            return self.response(dumps_networkapi(eventlog_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except (EventLogError):
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get API's version

        URLs: /eventlog/version/
        """

        try:
            version = dict()
            version['api_version'] = API_VERSION
            return self.response(dumps_networkapi(version))
        except BaseException, e:
            return self.response_error(1)
