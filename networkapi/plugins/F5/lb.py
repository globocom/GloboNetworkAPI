import bigsuds
import logging
from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins import F5

log = logging.getLogger(__name__)


class Lb(object):

    def __init__(self, hostname, username, password):

        self._hostname = hostname
        self._username = username

        try:
            self._channel = bigsuds.BIGIP(
                hostname=hostname,
                username=username,
                password=password
            )
        except Exception, e:
            logging.critical("Unable to connect to BIG-IP. Details: %s" % (e))
            raise base_exceptions.CommandErrorException(e)
        else:
            self._version = self._channel.System.SystemInfo.get_version()            
            if self._version[8:len(self._version)].split('.')[0] <= 10:
                raise base_exceptions.UnsupportedVersion(
                    'This plugin only supports BIG-IP v11 or above')
            else:
                self._channel = self._channel.with_session_id()
