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

        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_networkipv4.json',
        'networkapi/api_network/fixtures/sanity/initial_vlan.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
        'networkapi/api_network/fixtures/sanity/initial_ipv4.json',
        'networkapi/api_network/fixtures/sanity/initial_vip_request_v4.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_vip.json',
        'networkapi/api_network/fixtures/sanity/initial_env_env_vip.json',
        'networkapi/api_network/fixtures/sanity/initial_equipments.json',
        'networkapi/api_network/fixtures/sanity/initial_equipments_env.json',
        'networkapi/api_network/fixtures/sanity/initial_equipments_group.json',
        'networkapi/api_network/fixtures/sanity/initial_ipv4_eqpt.json',
        'networkapi/api_network/fixtures/sanity/initial_roteiros.json',
        'networkapi/api_network/fixtures/sanity/initial_equip_marca_model.json',
        verbosity=1
    )


class NetworkIPv4PutTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_try_update_nonexistent_netipv4(self):

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/net_nonexistent.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/1000/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

    def test_try_update_inactive_netipv4(self):
        """Tries to update inactive Network IPv4 changing cluster unit, network type and environment vip. NAPI should allow this request."""

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/net_inactive.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        name_file_get = 'api_network/tests/v3/sanity/networkipv4/json/get/basic/net_inactive.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file_get, response.data['networks'])

    def test_try_update_active_netipv4(self):
        """Tries to update active Network IPv4 changing cluster unit, network type and environment vip. NAPI should allow this request."""

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/net_active.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/1/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/1/?kind=basic&include=cluster_unit,active'
        name_file_get = 'api_network/tests/v3/sanity/networkipv4/json/get/basic/net_active.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file_get, response.data['networks'])

    def test_try_update_inactive_netipv4_changing_octets(self):
        """Tries to update inactive Network IPv4 changing octets. NAPI should deny or allow this request but without change octets."""

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/net_inactive_changing_octets.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        name_file_get = 'api_network/tests/v3/sanity/networkipv4/json/get/basic/net_inactive_changing_octets.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file_get, response.data['networks'])

    def test_try_update_inactive_netipv4_changing_nettype_to_none(self):
        """Tries to update inactive Network IPv4 changing network type to None. NAPI should deny or ignore this request."""

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/net_inactive_changing_net_type.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        name_file_get = 'api_network/tests/v3/sanity/networkipv4/json/get/basic/net_inactive_changing_net_type.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file_get, response.data['networks'])
