import logging

from adx import ClientCache

from networkapi.plugins import exceptions as base_exceptions

log = logging.getLogger(__name__)


class Lb(object):

    def __init__(self, hostname, username, password):

        self._hostname = hostname
        self._username = username

        try:
            device = {
                'management_ip': hostname,
                'user': username,
                'password': password
            }

            service_clients = (ClientCache
                               .get_adx_service_client(device))
            self.slb_factory = service_clients[0].factory
            self.slb_service = service_clients[0].service

            self.sys_factory = service_clients[1].factory
            self.sys_service = service_clients[1].service

            self.net_factory = service_clients[2].factory
            self.net_service = service_clients[2].service

        except Exception, e:
            logging.critical("Unable to connect to BROCADE. Details: %s" % (e))
            raise base_exceptions.CommandErrorException(e)
