# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads, XMLError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize, is_valid_int_greater_zero_param
from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectError, HealthcheckEqualError
from networkapi.ambiente.models import Ambiente, AmbienteNotFoundError


class HealthcheckAddResource(RestResource):

    log = Log('HealthcheckAddResource.')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add a HeltcheckExpect.

        URL: healthcheckexpect/add/
        """

        try:
            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            healthcheck_map = networkapi_map.get('healthcheck')
            if healthcheck_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            match_list = healthcheck_map.get('match_list')
            expect_string = healthcheck_map.get('expect_string')
            environment_id = healthcheck_map.get('id_ambiente')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            if expect_string is not None:
                if not is_valid_string_maxsize(expect_string, 50) or not is_valid_string_minsize(expect_string, 2):
                    self.log.error(
                        u'Parameter expect_string is invalid. Value: %s.', expect_string)
                    raise InvalidValueError(
                        None, 'expect_string', expect_string)
            else:
                raise InvalidValueError(None, 'expect_string', expect_string)

            if match_list is not None:
                if not is_valid_string_maxsize(match_list, 50) or not is_valid_string_minsize(match_list, 2):
                    self.log.error(
                        u'Parameter match_list is invalid. Value: %s.', match_list)
                    raise InvalidValueError(None, 'match_list', match_list)
            else:
                raise InvalidValueError(None, 'expect_string', expect_string)

            # User permission
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            healthcheck = HealthcheckExpect()

            ambiente = Ambiente.get_by_pk(environment_id)

            healthcheck.insert(user, match_list, expect_string, ambiente)

            healtchcheck_dict = dict()
            healtchcheck_dict['id'] = healthcheck.id

            return self.response(dumps_networkapi({'healthcheck_expect': healtchcheck_dict}))

        except AmbienteNotFoundError, e:
            return self.response_error(112)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except HealthcheckEqualError, e:
            return self.response_error(313, e.message)

        except HealthcheckExpectError, e:
            return self.response_error(1)

        except XMLError, e:
            return self.response_error(1)
