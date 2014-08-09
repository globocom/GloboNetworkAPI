# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import Ipv6, IpError, Ip, IpNotFoundError, IP_VERSION
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.exception import InvalidValueError
from networkapi.util import is_valid_ip_ipaddr
from django.forms.models import model_to_dict


class IpGetOctBlockResource(RestResource):

    log = Log('IpGetOctBlockResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Handles POST requests to get an IPv4 or Ipv6 by oct or blocks .

        URL: ip/getbyoctblock/
        '''

        self.log.info("Get a Ipv4's or Ipv6's")

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
            ip_map = networkapi_map.get('ip_map')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            ip = ip_map.get('ip')

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.IPS,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Valid ip
            if not is_valid_ip_ipaddr(ip):
                self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                raise InvalidValueError(None, 'ip', ip)

            # Business Rules
            version = ""
            ip_list = ip.split(".")

            if len(ip_list) == 1:

                ip_list = ip.split(":")
                ips = Ipv6.get_by_blocks(
                    ip_list[0],
                    ip_list[1],
                    ip_list[2],
                    ip_list[3],
                    ip_list[4],
                    ip_list[5],
                    ip_list[6],
                    ip_list[7])
                version = IP_VERSION.IPv6[1]

            else:

                ips = Ip.get_by_octs(
                    ip_list[0],
                    ip_list[1],
                    ip_list[2],
                    ip_list[3])
                version = IP_VERSION.IPv4[1]

            ips_list = []
            for ip in ips:
                ip_dict = model_to_dict(ip)
                ip_dict["version"] = version
                ips_list.append(ip_dict)

            return self.response(dumps_networkapi({'ips': ips_list}))

        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except IpNotFoundError:
            return self.response_error(119)

        except (IpError):
            return self.response_error(1)
