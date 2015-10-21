from networkapi.api_rest import exceptions as api_exceptions
from networkapi.plugins import exceptions as base_exceptions
import logging
from ..base import BasePlugin
import json

from networkapi.plugins.F5 import lb, poolmember

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    def connect(self, **kwargs):

        self._lb = lb.Lb(kwargs.get('fqdn'), kwargs.get('user'), kwargs.get('password'))


    ######################################
    # POOLMEMBER
    #######################################
    def setStateMember(self, pools):
        self.connect(
            fqdn=pools['fqdn'],
            user=pools['user'],
            password=pools['password'])

        pl = poolmember.PoolMember(self._lb)
        pl.setStates(pools)

    def getStateMember(self, pools):
        self.connect(
            fqdn=pools['fqdn'],
            user=pools['user'],
            password=pools['password'])

        pl = poolmember.PoolMember(self._lb)
        return pl.getStates(pools)

    def getStatusName(self, status):
        try:
            return poolmember.STATUS_POOL_MEMBER[status]
        except Exception, e:
            log.error('Member status invalid: %s' % (status))
            raise base_exceptions.MemberStatusCodeInvalid()
