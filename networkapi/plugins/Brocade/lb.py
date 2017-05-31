# -*- coding: utf-8 -*-
import logging

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.Brocade.adx_service import ClientCache

log = logging.getLogger(__name__)


class Lb(object):

    def __init__(self, hostname, username, password):

        self._hostname = hostname
        self._username = username
        self.service_clients = None

        try:
            device = {
                'management_ip': hostname,
                'user': username,
                'password': password
            }

            self.service_clients = (ClientCache
                                    .get_adx_service_client(device))
        except Exception, e:
            logging.critical('Unable to connect to BROCADE. Details: %s' % (e))
            raise base_exceptions.CommandErrorException(e)

        log.info('connected in hostname:%s' % hostname)
