# -*- coding: utf-8 -*-
import json

from django.test.client import Client
from mock import patch

from networkapi.test.mock import MockPluginNetwork
from networkapi.test.test_case import NetworkApiTestCase


class NetworkIPv4PostSuccessTestCase(NetworkApiTestCase):

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

        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
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

    def test_try_create_netipv4_with_octs(self):
        """Test of success to create a Network IPv4 with octs."""

        name_file = self.json_path % 'post/net_with_octs.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic' % response.data[0]['id']

        name_file_get = self.json_path % 'get/basic/net_with_octs.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file_get, response.data['networks'])

    def test_try_create_netipv4_with_octs_and_env_vip(self):
        """Test of success to create a Network IPv4 with octs and Environment Vip."""

        name_file = self.json_path % 'post/net_with_octs_env_vip.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic' % response.data[0]['id']

        name_file = self.json_path % 'get/basic/net_with_octs_env_vip.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file, response.data['networks'])

    def test_try_create_netipv4_with_auto_alloc(self):
        """Test of success to create a Network IPv4 without octs."""

        name_file_post = self.json_path % 'post/net_without_octs.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/',
            data=json.dumps(self.load_json_file(name_file_post)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic' % response.data[0]['id']

        name_file = self.json_path % 'get/basic/net_without_octs.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file, response.data['networks'])

    def test_try_create_netipv4_with_true_active_flag_being_ignored(self):
        """Test of success to create NetworkIPv4 with true active flag.
           Network must be created with active flag set as False.
        """
        name_file_post = self.json_path % 'post/net_with_active_flag_true.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/',
            data=json.dumps(self.load_json_file(name_file_post)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic&include=active' \
                  % response.data[0]['id']

        name_file = self.json_path % 'get/basic/net_with_active_flag_false.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file, response.data['networks'])


class NetworkIPv4DeploySuccessTestCase(NetworkApiTestCase):

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

        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
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

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_try_deploy_inactive_netipv4(self, test_patch):
        """Test of success to deploy a inactive NetworkIPv4."""

        mock = MockPluginNetwork()
        mock.status(True)
        test_patch.return_value = mock

        response = self.client.post(
            '/api/v3/networkv4/deploy/3/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v3/networkv4/3/?fields=active',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        active = response.data['networks'][0]['active']
        self.compare_values(True, active)


class NetworkIPv4PostErrorTestCase(NetworkApiTestCase):

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
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    # def test_try_create_netipv4_with_auto_alloc_in_full_env(self):
    #     """Test of error to create a Network IPv4 without octs in vlan of
    #        Environment with not available Network IPv4.
    #     """
    #
    #     name_file = self.json_path % 'post/net_without_octs_full_env.json'
    #
    #     # Does POST request
    #     response = self.client.post(
    #         '/api/v3/networkv4/',
    #         data=json.dumps(self.load_json_file(name_file)),
    #         content_type='application/json',
    #         HTTP_AUTHORIZATION=self.authorization)
    #
    #     self.compare_status(400, response.status_code)
    #
    #     self.compare_values(
    #         'Unavailable address to create a NetworkIPv4.',
    #         response.data['detail'])

    # def test_try_create_netipv4_with_octs_in_full_env(self):
    #     """Test of error to create a Network IPv4 with octs in vlan of
    #        Environment with not available Network IPv4.
    #     """
    #
    #     name_file = self.json_path % 'post/net_with_octs_full_env.json'
    #
    #     # Does POST request
    #     response = self.client.post(
    #         '/api/v3/networkv4/',
    #         data=json.dumps(self.load_json_file(name_file)),
    #         content_type='application/json',
    #         HTTP_AUTHORIZATION=self.authorization)
    #
    #     self.compare_status(400, response.status_code)
    #
    #     msg = 'One of the equipment associated with the environment of this ' \
    #         'Vlan is also associated with other environment that has a ' \
    #         'network with the same track, add filters in environments if ' \
    #         'necessary. Your Network: 10.10.6.0/24, Network already created:' \
    #         ' 10.10.6.0/24'
    #
    #     self.compare_values(msg, response.data['detail'])

    def test_try_create_netipv4_out_of_range_with_octs(self):
        """Test of error to create a Network IPv4 with octs out of range
           configuration defined in related vlan of Environment.
        """

        name_file = self.json_path % 'post/net_with_octs_out_of_range.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)

        msg = 'Network 172.10.6.0/24 cannot not inserted in environment ' \
            'BE-TESTE-2 - TESTE - BALANCEAMENTO-POOL because it is not ' \
            'within environment network range.'

        self.compare_values(msg, response.data['detail'])


class NetworkIPv4DeployErrorTestCase(NetworkApiTestCase):

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

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_try_deploy_active_netipv4(self, test_patch):
        """Test of error to deploy a active NetworkIPv4."""

        mock = MockPluginNetwork()
        mock.status(False)
        test_patch.return_value = mock

        url_post = '/api/v3/networkv4/deploy/1/'

        response = self.client.post(
            url_post,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(400, response.status_code)

        self.compare_values(
            'Already Active Network. Nothing to do.', response.data['detail'])

        url_get = '/api/v3/networkv4/1/?fields=active'

        response = self.client.get(
            url_get,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        active = response.data['networks'][0]['active']
        self.compare_values(True, active)


class NetworkIPv4ForcePostSuccessTestCase(NetworkApiTestCase):

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

        'networkapi/api_network/fixtures/sanity/initial_environment.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_dc.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/sanity/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_ipconfig.json',
        'networkapi/api_network/fixtures/sanity/initial_config_environment.json',
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
        self.authorization = self.get_http_authorization('test_admin')

    def tearDown(self):
        pass

    def test_try_create_netipv4_without_active_flag(self):
        """Test of success to create NetworkIPv4 without active flag.
           By default, active flag must be set to false.
        """

        name_file = self.json_path % 'post/net_without_active_flag.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/force/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic&include=active' % response.data[
            0]['id']

        name_file_get = self.json_path % 'get/basic/net_with_active_flag_false.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file_get, response.data['networks'])

    def test_try_create_netipv4_with_active_flag_equals_to_true(self):
        """Test of success to create NetworkIPv4 with active flag set to true."""

        name_file = self.json_path % 'post/net_with_active_flag_true.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/force/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic&include=active' % response.data[
            0]['id']

        name_file_get = self.json_path % 'get/basic/net_with_active_flag_true.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file_get, response.data['networks'])

    def test_try_create_netipv4_with_active_flag_equals_to_false(self):
        """Test of success to create NetworkIPv4 with active flag set to false."""

        name_file = self.json_path % 'post/net_with_active_flag_false.json'

        # Does POST request
        response = self.client.post(
            '/api/v3/networkv4/force/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v3/networkv4/%s/?kind=basic&include=active' % response.data[
            0]['id']

        name_file_get = self.json_path % 'get/basic/net_with_active_flag_false.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        del response.data['networks'][0]['id']
        self.compare_json(name_file_get, response.data['networks'])
