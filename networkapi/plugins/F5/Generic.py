from networkapi.api_rest import exceptions as api_exceptions
from networkapi.plugins import exceptions as base_exceptions
import logging
from ..base import BasePlugin
import json

from networkapi.plugins.F5 import lb, pool, poolmember, util

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    #######################################
    # POOLMEMBER
    #######################################
    @util.transation
    def setStateMember(self, pools):

        pls = util._trataParam(pools)

        plm = poolmember.PoolMember(self._lb)

        plm.setStates(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            monitor_state=pls['pools_members']['monitor'],
            session_state=pls['pools_members']['session'])

    @util.transation
    def setConnectionLimitMember(self, pools):

        pls = util._trataParam(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setConnectionLimit(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            connection_limit=pls['pools_members']['limit'])

    @util.transation
    def setPriorityMember(self, pools):

        pls = util._trataParam(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setPriority(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            priority=pls['pools_members']['priority'])

    @util.transation
    def getStateMember(self, pools):
        pls = util._trataParam(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.getStates(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @util.transation
    def createMember(self, pools):

        pls = util._trataParam(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.create(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @util.transation
    def removeMember(self, pools):

        pls = util._trataParam(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.remove(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])


    #######################################
    # POOL
    #######################################
    @util.transation
    def createPool(self, pools):

        pls = util._trataParam(pools)

        pl = pool.Pool(self._lb)

        pl.create(
            names=pls['pools_names'],
            lbmethod=pls['pools_lbmethod'],
            members=pls['pools_members']['members'])

        pl.setServiceDownAction(
            names=pls['pools_names'],
            actions=pls['pools_actions'])

        pl.setMonitorAssociation(
            names=pls['pools_names'],
            healthcheck=pls['pools_healthcheck'])

        plm = poolmember.PoolMember(self._lb)
        
        plm.setConnectionLimit(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            connection_limit=pls['pools_members']['limit'])

        plm.setPriority(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            priority=pls['pools_members']['priority'])

        plm.setStates(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            monitor_state=pls['pools_members']['monitor'],
            session_state=pls['pools_members']['session'])
