# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.api_ip import facade
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.ip.models import IpNotFoundError
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class IPv6FunctionalTestV3(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')
        self.url_prefix = '/api/v3/ipv6/%s/'
        self.status_code_msg = 'Status code should be %s and was %s'

    def tearDown(self):
        pass

    def test_get_ipv6(self):

        pass
