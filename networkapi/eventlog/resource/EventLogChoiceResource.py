# -*- coding:utf-8 -*-

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads
from networkapi.eventlog.models import EventLog, EventLogError, Functionality


def ValuesQuerySetToList(vqs):
    data = list()
    for item in vqs:
        data += item
    return data


def FunctionalitiesList(fl):
    data = list()
    for item in fl:
        func = dict()
        func['f_value'] = item.nome
        func['f_name'] = item.nome
        data.append(func)
    data.insert(0, {'f_value': '0', 'f_name': '-'})
    return data


def UsersList(ul):
    data = list()
    for item in ul:
        user = dict()
        user['id_usuario'] = item.usuario.id
        user['nome'] = item.usuario.nome
        user['usuario'] = item.usuario.user
        data.append(user)
    data.insert(0, {'id_usuario': '0', 'nome': '-', 'usuario': '-'})
    return data


class EventLogChoiceResource(RestResource):
    log = Log('EventLogFindResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to find all logs by search parameters.

        URLs: /eventlog/find/
        """

        self.log.info('find all logs')

        try:
            # Common validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.USER_ADMINISTRATION,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    'User does not have permission to perform this operation.')
                return self.not_authorized()

            # Business Validations

            # Here starts the stuff

            functionalities = Functionality.objects

            acoes = ['Cadastrar', 'Alterar', 'Remover']
            usuarios = EventLog.uniqueUsers()
            funcionalidades = functionalities.all()

            usuarios = UsersList(usuarios)
            funcionalidades = FunctionalitiesList(funcionalidades)

            choices_map = dict()

            choices_map['usuario'] = usuarios
            choices_map['acao'] = acoes
            choices_map['funcionalidade'] = funcionalidades

            return self.response(dumps_networkapi(choices_map))

        except InvalidValueError as e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.',
                e.param,
                e.value)
            return self.response_error(269, e.param, e.value)
        except (EventLogError):
            return self.response_error(1)
        except BaseException as e:
            return self.response_error(1)
