# -*- coding: utf-8 -*-
from django.test.client import Client
from mock import patch

from networkapi.api_network import tasks
from networkapi.test.mock import MockPluginNetwork
from networkapi.test.test_case import NetworkApiTestCase


class NetworkIPv4AsyncDeleteSuccessTestCase(NetworkApiTestCase):

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

    def test_task_id_create_in_delete_one_netipv4_success(self):
        """Test success of id task generate for netipv4 delete."""

        obj_id = 5
        response = tasks.delete_networkv4.apply(args=[obj_id],
                                                queue='napi.network')

        id_task = response.id
        self.compare_values(36, len(id_task))
