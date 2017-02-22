# -*- coding: utf-8 -*-
import json
import logging
import sys
from itertools import izip
from time import time

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger()
log.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stream_handler)


def setup():
    call_command(
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/vlan/fixtures/initial_tipo_rede.json',
        'networkapi/filter/fixtures/initial_filter.json',
        'networkapi/filterequiptype/fixtures/initial_filterequiptype.json',
        'networkapi/equipamento/fixtures/initial_tipo_equip.json',
        'networkapi/equipamento/fixtures/initial_equip_marca.json',
        'networkapi/equipamento/fixtures/initial_equip_model.json',

        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_networkipv6.json',
        'networkapi/api_network/fixtures/sanity/initial_vlan.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
        'networkapi/api_network/fixtures/sanity/initial_ipv6.json',
        'networkapi/api_network/fixtures/sanity/initial_vip_request_v6.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_vip.json',
        'networkapi/api_network/fixtures/sanity/initial_env_env_vip.json',

        verbosity=1
    )


class NetworkIPv6DeleteTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_try_delete_inactive_netipv6(self):
        """Tries to delete an inactive Network IPv6 without IP Addresses. NAPI should allow this request."""

        delete_url = '/api/v3/networkv6/5/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv6/5/'

        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv6 with pk = 5.',
            response.data['detail']
        )

    def test_try_delete_active_netipv6(self):
        """Tries to delete an active Network IPv6 without IP Addresses. NAPI should deny this request."""

        delete_url = '/api/v3/networkv6/1/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(500, response.status_code)

        get_url = '/api/v3/networkv6/1/?kind=basic'

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/get/basic/pk_1.json'

        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_delete_inactive_netipv6_with_ip_assoc_to_active_vip(self):
        """Tries to delete an inactive Network IPv6 with only one IP address associated to an active VIP Request. NAPI should deny this request."""

        delete_url = '/api/v3/networkv6/3/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(500, response.status_code)

        get_url = '/api/v3/networkv6/3/?kind=basic'

        name_file = 'api_network/tests/v3/sanity/networkipv6/json/delete/basic/pk_3.json'

        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_delete_inactive_netipv6_with_ip_assoc_to_inactive_vip(self):
        """Tries to delete an inactive Network IPv6 with only one IP address associated to an active VIP Request. NAPI should allow this request."""

        delete_url = '/api/v3/networkv6/4/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv6/4/'

        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv6 with pk = 4.',
            response.data['detail']
        )

    def test_try_delete_inactive_netipv6_with_ips(self):
        """Tries to delete a Network IPv6 with two IP Addresses not associated to any active VIP Request. NAPI should allow this request."""

        delete_url = '/api/v3/networkv6/6/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv6/6/'

        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no NetworkIPv6 with pk = 6.',
            response.data['detail']
        )
