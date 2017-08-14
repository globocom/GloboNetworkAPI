from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring
from collections import OrderedDict
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.Dell.FTOS.BGP.exceptions import InvalidNeighborException
from networkapi.plugins import exceptions
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from schema import Schema
from schema import SchemaError
from schema import SchemaWrongKeyError
from schema import And
from schema import Use
from schema import Optional

log = logging.getLogger(__name__)

map_fields = {
    'remote_ip': 'neighbor-router',
    'remote_as': 'remote-as' ,
    'password' : {
        'password': 'password-value'
    },
    'maximum_hops': 'ebgp-multihop',
    'timer_keepalive': {
        'timers': 'keepalive'
    },
    'timer_timeout': {
        'timers': 'hold-time'
    },
    'description': 'description',
    'soft_reconfiguration': 'soft-reconfiguration',
    'community': 'send-community',
    'remove_private_as': 'remove-private-as',
    'next_hop_self': 'next-hop-self'
}

class Generic(object):

    def __init__(self, equipment=None, neighbor=None):

        self.equipment = equipment
        self.neighbor = neighbor
        self.equipment_access = None

    def _process_neighbor(self):
        """Validate and Change Neighbor input because some tags can't might be
           present when these tags are False.
        """

        self._validate_neighbor()
        self._treat_soft_reconfiguration()
        self._treat_community()
        self._order_neighbor()

    def _validate_neighbor(self):
        """Validate neighbor against Schema."""

        neighbor_schema = Schema({
            'remote_ip': basestring,
            'remote_as': And(basestring, lambda n: 0 <= int(n) <= 4294967295),
            Optional('password'): basestring,
            Optional('maximum_hops'): And(basestring,
                                          lambda n: 1 <= int(n) <= 255),
            Optional('timer_keepalive'): And(basestring,
                                             lambda n: 1 <= int(n) <= 65535),
            Optional('timer_timeout'): And(basestring,
                                           lambda n: 3 <= int(n) <= 65536),
            Optional('description'): basestring,
            Optional('soft_reconfiguration'): bool,
            Optional('community'): bool,
            Optional('remove_private_as'): bool,
            Optional('next_hop_self'): bool
        })

        try:
            neighbor_schema.validate(self.neighbor)
        except SchemaWrongKeyError:
            # It doesn't matter if neighbor dict has other keys besides these.
            pass
        except SchemaError as e:
            raise InvalidNeighborException(e.code)

    def _treat_soft_reconfiguration(self):

        if self.neighbor.get('soft_reconfiguration') is True:
            self.neighbor['soft_reconfiguration'] = 'inbound'
        elif self.neighbor.get('soft_reconfiguration') is False:
            del self.neighbor['soft_reconfiguration']

        # If soft_reconfiguration is not present, anything happens

    def _treat_community(self):

        if self.neighbor.get('community') is True:
            self.neighbor['community'] = ''
        elif self.neighbor.get('community') is False:
            del self.neighbor['community']

        # If community is not present, anything happens

    def _order_neighbor(self):
        """Reorder fields in neighbor dict transforming it later
           in an OrderedDict.
        """

        remote_ip = self.neighbor['remote_ip']
        del self.neighbor['remote_ip']

        self.neighbor = OrderedDict(self.neighbor)

        # When generate XML, remote_ip should be the first
        self.neighbor.update({'remote_ip': remote_ip})

    def _dict_to_xml(self):

        self._process_neighbor()

        bgp_xml = Element('bgp')

        as_xml = SubElement(bgp_xml, 'as-name')
        as_xml.text = '65114'
        neighbor_xml = SubElement(bgp_xml, 'neighbor')

        # Walk the OrderedDict neighbor in Reversed Order to generate XML with
        # remote_ip in first position and remote_as in second position.
        for field in reversed(self.neighbor):

            if isinstance(map_fields.get(field), basestring):

                child_xml = SubElement(neighbor_xml, map_fields[field])
                child_xml.text = self._to_str(self.neighbor[field])

            elif isinstance(map_fields.get(field), dict):

                for child in map_fields[field]:

                    child_xml = self._create_or_get_element(neighbor_xml,
                                                            child)

                    child_of_child_xml = SubElement(child_xml,
                                                    map_fields[field][child])
                    child_of_child_xml.text = self._to_str(self.neighbor[field])

        return tostring(bgp_xml)

    def deploy_neighbor(self):

        path = "api/running/dell/router/bgp/"
        data = self._dict_to_xml()
        self._request(method='patch', path=path, data=data, content_type='xml')

    def undeploy_neighbor(self):

        path = "api/running/dell/router/bgp/{}/neighbor/{}/".\
            format(65114,
                   self.neighbor['remote_ip'])
        data = self._dict_to_xml()
        self._request(method='delete', path=path, data=data, content_type='xml')

    def _request(self, **kwargs):

        # Params and default values
        params = {
            'method': None,
            'path': None,
            'data': None,
            'content_type': None,
        }

        # Setting params via kwargs or use the defaults
        for param in params:
            if param in kwargs:
                params[param] = kwargs.get(param)

        headers = self._get_headers(content_type=params['content_type'])
        uri = self._get_uri(path=params['path'])

        log.info(
            'Starting %s request to equipment %s at %s. Data to be sent: %s' %
            (params['method'], self.equipment.nome, uri, params['data'])
            )

        try:
            # Raises AttributeError if method is not valid
            func = getattr(requests, params['method'])

            request = func(
                uri,
                auth=self._get_auth(),
                headers=headers,
                data=params['data']
            )

            request.raise_for_status()

            try:
                return request.text
            except:
                return

        except AttributeError:
            log.error('Request method must be valid HTTP request. '
                      'ie: GET, POST, PUT, DELETE')
        except HTTPError:
            try:
                response = request.text

            except:
                log.error("Unknown error during request to Dell Equipment.")

            raise HTTPError("%s - %s" % (request.status_code, request.text))

    def _get_auth(self):
        return self._basic_auth()

    def _basic_auth(self):
        return HTTPBasicAuth(
            self.equipment_access.user,
            self.equipment_access.password
        )

    def _get_headers(self, content_type):
        types = {
            'xml':  'application/vnd.yang.data+xml',
            'text': 'text/plain'
        }

        return {'Content-Type': types[content_type]}

    def _get_equipment_access(self, protocol):
        try:
            return EquipamentoAcesso.search(
                None, self.equipment, protocol).uniqueResult()
        except Exception:
            log.error('Access type %s not found for equipment %s.' %
                      ('http', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()

    def _get_host(self):

        protocol = 'http'
        self.equipment_access = self._get_equipment_access(protocol)
        if not isinstance(self.equipment_access, EquipamentoAcesso):

            log.error('No fqdn could be found for equipment %s .' %
                      (self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()

        host = self.equipment_access.fqdn.strip()
        if host.find('://') < 0:
            host = protocol + '://' + host + ':8008'

        return host

    def _get_uri(self, host=None, path=""):

        if host is None:
            host = self._get_host()

        host = host.strip()
        path = path.strip()

        if host[len(host) - 1] == '/':
            host = host[0:len(host) - 1]
        if path[0] == '/':
            path = path[1:len(path)]
        self.uri = host + '/' + path

        return self.uri

    @staticmethod
    def _create_or_get_element(root, tag):

        if root.find(tag) is not None:
            return root.find(tag)
        else:
            return SubElement(root, tag)

    @staticmethod
    def _to_str(value):

        if isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

