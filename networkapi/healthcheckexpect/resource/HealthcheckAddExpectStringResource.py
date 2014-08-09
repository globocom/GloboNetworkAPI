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
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize
from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectError, HealthcheckEqualError


class HealthcheckAddExpectStringResource(RestResource):

    log = Log('HealthcheckAddExpectStringResource.')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add a HeltcheckExpect only expect_string field.

        URL: healthcheckexpect/add/expectstring/
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

            expect_string = healthcheck_map.get('expect_string')
            if not is_valid_string_maxsize(expect_string, 50):
                self.log.error(
                    u'Parameter expect_string is invalid. Value: %s.',
                    expect_string)
                raise InvalidValueError(None, 'expect_string', expect_string)

            # User permission
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            healthcheck = HealthcheckExpect()

            healthcheck.insert_expect_string(user, expect_string)

            healtchcheck_dict = dict()
            healtchcheck_dict['id'] = healthcheck.id

            return self.response(
                dumps_networkapi({'healthcheck_expect': healtchcheck_dict}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except HealthcheckEqualError as e:
            return self.response_error(313, e.message)

        except HealthcheckExpectError as e:
            return self.response_error(1)

        except XMLError as e:
            return self.response_error(1)
