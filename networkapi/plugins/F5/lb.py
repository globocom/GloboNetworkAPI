# -*- coding:utf-8 -*-
import logging
from time import sleep

import bigsuds

from networkapi.plugins import exceptions as base_exceptions

log = logging.getLogger(__name__)


class Lb(object):

    def __init__(self, hostname, username, password, session=True):

        self._hostname = hostname
        self._username = username
        self._password = password
        self._time_reconn = 10

        try:
            self._channel = bigsuds.BIGIP(
                hostname=self._hostname,
                username=self._username,
                password=self._password
            )

        except Exception, e:
            logging.critical("Unable to connect to BIG-IP. Details: %s" % (e))
            raise base_exceptions.CommandErrorException(e)
        else:
            log.info('Connected in hostname:%s' % hostname)
            try:
                self._version = self._channel.System.SystemInfo.get_version()

                if self._version[8:len(self._version)].split('.')[0] <= 10:
                    raise base_exceptions.UnsupportedVersion(
                        'This plugin only supports BIG-IP v11 or above')
                else:
                    if session:
                        log.info('Try get new session')
                        session_cur = self._channel.System.Session.get_session_timeout()
                        log.info('Session Timeout Current: %s' % session_cur)
                        if int(session_cur) > 60:
                            self._channel.System.Session.set_session_timeout(60)
                        self._channel = self.get_session()
            except Exception, e:
                log.error(e)
                raise base_exceptions.CommandErrorException(e)
        finally:
            log.info('Disconnected of hostname:%s' % hostname)

    def get_session(self):

        try:
            channel = self._channel.with_session_id()
            log.info('Session %s', channel)
        except Exception, e:
            if 'There are too many existing user sessions.'.lower() in str(e).lower():
                self._time_reconn *= 2
                log.warning(
                    'There are too many existing user sessions. '
                    'Trying again in %s seconds' % self._time_reconn)
                sleep(self._time_reconn)
                self.get_session()
            else:
                raise e
        else:
            return channel
