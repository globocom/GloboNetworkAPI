# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from mock import patch, call, Mock, MagicMock
from networkapi.api_pools.exceptions import UpdateEnvironmentPoolCreatedException, UpdateEnvironmentVIPException, \
    UpdateEnvironmentServerPoolMemberException, ScriptAlterLimitPoolException, ScriptAlterLimitPoolDiffMembersException, \
    ScriptCreatePoolException, ScriptAlterServiceDownActionException, InvalidRealPoolException, \
    ScriptAlterPriorityPoolMembersException
from networkapi.api_pools.facade import *
from networkapi.api_pools.models import OptionPool
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.ip.models import Ip, Ipv6
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember
from networkapi.usuario.models import Usuario
from networkapi.util import is_valid_healthcheck_destination

class PoolTest(unittest.TestCase):

    def setUp(self):
        self.user = Usuario(id = 1, nome = 'users')
        self.mock_transaction()

    def test_ederson(self):

        health_check = get_or_create_healthcheck(self.user, 'WORKING', 'HTTP', '/healthcheck', '*:*', '1')

        self.assertEquals('WORKING', health_check.healthcheck_expect)
        self.assertEquals('HTTP', health_check.healthcheck_type)
        self.assertEquals('/healthcheck', health_check.healthcheck_request)
        self.assertEquals('*:*', health_check.destination)
        self.assertEquals('1', health_check.identifier)
        self.assertIsNotNone(health_check)

    def mock_transaction(self):
        patch('networkapi.api_pools.facade.transaction').start()


    #MOCKS
    def mock_find_healthcheck(self, response):
        mock = patch("networkapi.healthcheckexpect.models.Healthcheck.objects.get").start()
        if issubclass(response.__class__, Exception):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock

    def mock_healthcheck_save(self):
        return patch("networkapi.healthcheckexpect.models.Healthcheck.save").start()
