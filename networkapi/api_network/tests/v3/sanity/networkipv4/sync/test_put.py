# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase


class NetworkIPv4PutSuccessTestCase(NetworkApiTestCase):

    fixtures = [
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
        'networkapi/api_network/fixtures/sanity/initial_cidr.json',

    ]

    json_path = 'api_network/tests/v3/sanity/networkipv4/json/%s'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_try_update_inactive_netipv4(self):
        """Test of success to update inactive Network IPv4 changing cluster unit,
           network type and environment vip.
        """

        name_file = self.json_path % 'put/net_inactive.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        name_file = self.json_path % 'get/basic/net_inactive.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_update_active_netipv4(self):
        """Test of success to update active Network IPv4 changing cluster unit,
           network type and environment vip.
        """

        name_file = self.json_path % 'put/net_active.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/1/?kind=basic&include=cluster_unit,active'
        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        name_file = self.json_path % 'get/basic/net_active.json'
        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_update_inactive_netipv4_changing_octets(self):
        """Test of success to update inactive Network IPv4 changing octets.
           Octets will not be changed.
        """

        name_file_put = self.json_path % 'put/net_inactive_changing_octets.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        name_file = self.json_path % 'get/basic/net_inactive_changing_octets.json'
        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_update_netipv4_ignore_change_active_flag_from_false_to_true(self):
        """Test of success to update NetworkIPv4 changing active flag from False
           to True. Active flag cannot be changed.
        """
        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/' \
                        'net_changing_active_from_false_to_true.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        name_file = self.json_path % 'get/basic/net_inactive.json'
        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_update_netipv4_ignore_change_active_flag_from_true_to_false(self):
        """Test of success to update NetworkIPv4 changing active flag from True.
           to False. Active flag cannot be changed.
        """
        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/' \
                        'net_changing_active_from_true_to_false.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/1/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/1/?kind=basic&include=cluster_unit,active'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        name_file = self.json_path % 'get/basic/net_active.json'
        self.compare_json_lists(name_file, response.data['networks'])


class NetworkIPv4PutErrorTestCase(NetworkApiTestCase):

    fixtures = [
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
        'networkapi/api_network/fixtures/sanity/initial_equip_marca_model.json'
    ]

    json_path = 'api_network/tests/v3/sanity/networkipv4/json/%s'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_try_update_nonexistent_netipv4(self):
        """Test of error to update inexistent Network IPv4."""

        name_file = self.json_path % 'put/net_nonexistent.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/1000/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            'There is no NetworkIPv4 with pk = 1000.', response.data['detail'])

    def test_try_update_inactive_netipv4_changing_nettype_to_none(self):
        """Test of error to update inactive Network IPv4 changing network type
           to None.
        """

        name_file = self.json_path % 'put/net_inactive_changing_net_type.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/3/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)

        self.compare_values(
            ['Wrong type'],
            response.data['detail']['errors'][0]['error_reasons'])

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        name_file = self.json_path % 'get/basic/net_inactive_changing_net_type.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['networks'])


class NetworkIPv4ForcePutSuccessTestCase(NetworkApiTestCase):

    fixtures = [
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
        'networkapi/api_network/fixtures/sanity/initial_cidr.json'

    ]

    json_path = 'api_network/tests/v3/sanity/networkipv4/json/%s'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test_admin')

    def tearDown(self):
        pass

    def test_try_update_netipv4_changing_active_flag_from_false_to_true(self):
        """Test of success of changing NetworkIPv4 active flag from false
           to true without really deploy the Network.
        """

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/' \
                        'net_changing_active_from_false_to_true.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/force/3/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/3/?kind=basic&include=cluster_unit,active'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        name_file = self.json_path % 'get/basic/net_changed_active_from_false_to_true.json'
        self.compare_json_lists(name_file, response.data['networks'])

    def test_try_update_netipv4_changing_active_flag_from_true_to_false(self):
        """Test of success of changing NetworkIPv4 active flag from true
           to false without really undeploy the Network.
        """

        name_file_put = 'api_network/tests/v3/sanity/networkipv4/json/put/' \
                        'net_changing_active_from_true_to_false.json'

        # Does PUT request
        response = self.client.put(
            '/api/v3/networkv4/force/1/',
            data=json.dumps(self.load_json_file(name_file_put)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v3/networkv4/1/?kind=basic&include=cluster_unit,active'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        name_file = self.json_path % 'get/basic/net_changed_active_from_true_to_false.json'
        self.compare_json_lists(name_file, response.data['networks'])
