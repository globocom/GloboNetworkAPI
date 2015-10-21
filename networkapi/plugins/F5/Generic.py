from networkapi.api_rest import exceptions as api_exceptions
from networkapi.plugins import exceptions as base_exceptions
import logging
from ..base import BasePlugin
import json

from networkapi.plugins.F5 import lb, poolmember, util

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    ######################################
    # POOLMEMBER
    #######################################
    @util.transation
    def setStateMember(self, pools):

        pl = poolmember.PoolMember(self._lb)
        pl.setStates(pools)

    @util.transation
    def getStateMember(self, pools):

        pl = poolmember.PoolMember(self._lb)
        return pl.getStates(pools)

    @util.transation
    def createMember(self, pools):

        pl = poolmember.PoolMember(self._lb)
        return pl.create(pools)

    @util.transation
    def removeMember(self, pools):

        pl = poolmember.PoolMember(self._lb)
        return pl.remove(pools)

    def getStatusName(self, status):
        try:
            return poolmember.STATUS_POOL_MEMBER[status]
        except Exception, e:
            log.error('Member status invalid: %s' % (status))
            raise base_exceptions.MemberStatusCodeInvalid()
