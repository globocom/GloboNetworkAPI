# -*- coding:utf-8 -*-
'''
@author: William Vedroni da Silva
@organization: S2it
@copyright: 2014 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import ConfigEnvironmentInvalidError, IP_VERSION, \
    Ambiente, IPConfig, ConfigEnvironment, AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError, PermissionError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import IpError, NetworkIPv6Error, NetworkIPv4Error, NetworkIPRangeEnvError
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param, is_valid_version_ip, \
    is_valid_int_param
from networkapi.vlan.models import VlanError
from networkapi.vlan.resource.VlanFindResource import break_network
from string import split
from networkapi.vlan.models import TipoRede


class EnvironmentConfigurationAddResource(RestResource):

    log = Log('EnvironmentConfigurationAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to add new Environment Configuration Prefix

        URL: environment/configuration/add
        """

        try:

            self._validate_permission(user)

            xml_map, _ = loads(request.raw_post_data)

            networkapi_map = xml_map.get('networkapi')

            self._validate_xml_networkapi(networkapi_map)

            network_map = networkapi_map.get('ambiente')

            self._validate_xml_network(network_map)

            # Get XML data
            network = network_map.get('network')
            id_environment = network_map.get('id_environment')
            ip_version = network_map.get('ip_version')
            network_type = network_map.get('network_type')
            prefix = network_map.get('prefix')

            self._validate_network(network, prefix)

            self._validate_environment_id(id_environment)

            self._validate_ip_version(ip_version)

            self._validate_network_type(network_type)

            self._validate_prefix_by_net_type(prefix, ip_version)

            environment = Ambiente().get_by_pk(id_environment)

            network_type = TipoRede.get_by_pk(network_type)

            ip_config = IPConfig()
            ip_config.subnet = network
            ip_config.new_prefix = prefix
            ip_config.type = ip_version
            ip_config.network_type = network_type

            ip_config.save(user)

            config_environment = ConfigEnvironment()
            config_environment.environment = environment
            config_environment.ip_config = ip_config

            config_environment.save(user)

            return self.response(dumps_networkapi({'network': network_map}))

        except PermissionError:
            return self.not_authorized()

        except AmbienteNotFoundError, e:
            return self.response_error(112)

        except InvalidValueError, e:
            self.log.error(u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)

        except ConfigEnvironmentInvalidError, e:
            return self.response_error(294)

        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)

    """Validations"""

    def _validate_permission(self, user):

        if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.ENVIRONMENT_MANAGEMENT):
            self.log.error(u'User does not have permission to perform the operation.')
            raise PermissionError(None, None)

    def _validate_xml_networkapi(self, networkapi_map):

        if networkapi_map is None:
            msg = u'There is no value to the networkapi tag of XML request.'
            self.log.error(msg)
            raise XMLError(None, message=msg)

    def _validate_xml_network(self, network_map):

        if network_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                raise XMLError(None, message=msg)

    def _validate_ip_version(self, network_type):

        if not is_valid_version_ip(network_type, IP_VERSION):
            self.log.error(u'The type network parameter is invalid value: %s.', network_type)
            raise InvalidValueError(None, 'network_type', network_type)

    def _validate_environment_id(self, id_environment):

        if not is_valid_int_greater_zero_param(id_environment):
            self.log.error(u'The id_environment parameter is invalid value: %s.', id_environment)
            raise InvalidValueError(None, 'id_environment', id_environment)

    def _validate_network_type(self, network_type_id):

        if not is_valid_int_greater_zero_param(network_type_id):
            self.log.error(u'The network_type_id parameter is invalid value: %s.', network_type_id)
            raise InvalidValueError(None, 'network_type_id', network_type_id)

    def _validate_network(self, network, prefix):

        try:
            net = IPNetwork(network)
        except ValueError:
            self.log.error(u'The network parameter is invalid value: %s.', network)
            raise InvalidValueError(None, 'network', network)

        blocks, network, version = break_network(network)

        expl = split(net.network.exploded, "." if version == IP_VERSION.IPv4[0] else ":")
        expl.append(str(net.prefixlen))

        block = int(blocks[-1])

        if blocks != expl:
            raise InvalidValueError(None, 'network', network)

        if block > int(prefix):
            self.log.error(u'The block parameter is invalid value: %s.', block)
            raise InvalidValueError(None, 'block', block)

    def _validate_prefix_by_net_type(self, prefix, network_type):

        if is_valid_int_param(prefix):
            if network_type == IP_VERSION.IPv4[0]:
                if int(prefix) not in range(33):
                    self.log.error(u'The prefix parameter is invalid value: %s.', prefix)
                    raise InvalidValueError(None, 'prefix', prefix)
            elif network_type == IP_VERSION.IPv6[0]:
                if int(prefix) not in range(129):
                    self.log.error(u'The prefix parameter is invalid value: %s.', prefix)
                    raise InvalidValueError(None, 'prefix', prefix)
