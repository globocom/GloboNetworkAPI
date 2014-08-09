# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.rest import RestResource

from networkapi.auth import has_perm

from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectError

from networkapi.ambiente.models import Ambiente, AmbienteNotFoundError

from networkapi.admin_permission import AdminPermission

from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.grupo.models import GrupoError

from networkapi.util import is_valid_int_greater_zero_param

from networkapi.exception import InvalidValueError


class HealthcheckExpectResource(RestResource):

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para consulta de HealthCheckExpects.

        Lista as informações dos HealthCheckExpect's de um determinado ambiente.

        URL:  /healthcheckexpect/ambiente/<id_amb>/
        """
        try:
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            map_list = []

            environment_id = kwargs.get('id_amb')
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.',
                    environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            environment = Ambiente().get_by_pk(environment_id)

            healthcheckexpects = HealthcheckExpect().search(environment_id)

            for healthcheckexpect in healthcheckexpects:
                healthcheckexpect_map = dict()
                healthcheckexpect_map['id'] = healthcheckexpect.id
                healthcheckexpect_map[
                    'expect_string'] = healthcheckexpect.expect_string
                healthcheckexpect_map[
                    'match_list'] = healthcheckexpect.match_list
                healthcheckexpect_map[
                    'id_ambiente'] = healthcheckexpect.ambiente_id

                map_list.append(healthcheckexpect_map)

            return self.response(
                dumps_networkapi({'healthcheck_expect': map_list}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (HealthcheckExpectError, GrupoError):
            return self.response_error(1)
