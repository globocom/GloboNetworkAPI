# -*- coding: utf-8 -*-
import json
from itertools import izip

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

fixtures_base_path = 'networkapi/api_network/fixtures/integration/%s'


class NetworksIntegrationV6TestCase(NetworkApiTestCase):

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
        'networkapi/equipamento/fixtures/initial_equip_marca.json',
        'networkapi/equipamento/fixtures/initial_equip_model.json',

        fixtures_base_path % 'initial_vrf.json',
        fixtures_base_path % 'initial_environment_dc.json',
        fixtures_base_path % 'initial_environment_envlog.json',
        fixtures_base_path % 'initial_environment_gl3.json',
        fixtures_base_path % 'initial_environment.json',
        fixtures_base_path % 'initial_ipconfig.json',
        fixtures_base_path % 'initial_config_environment.json',
        fixtures_base_path % 'initial_equipments.json',
        fixtures_base_path % 'initial_equipments_env.json',
        fixtures_base_path % 'initial_vlan.json',
        fixtures_base_path % 'initial_cidrs.json',
    ]

    def setUp(self):

        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_create_networkv6_by_zero(self):
        """
        Test of integration for create environment, vlan, eqpt networks v6.

        ##################
        Starting test:
            - environment A:
                - eqpt 1, 2, 3
                - vrf 1
                - starting vlans 1,2,3
            - environment B:
                - eqpt 2, 4, 5
                - vrf 1
                - starting vLANS 4, 5, 6, 7, 8, 9
            - environment C:
                - EQpt 5, 6
                - vrf 2
                - startinG VLANS 10, 11
            - environment D:
                - eqpt 7
                - vrf 1
                - starting vlans 1
        ##################

        ##################
        Starting networks:
            environment A:
                Nothing
            environment B:
                fdbe:bebe:bebe:1201:0000:0000:0000:0000/64
                fdbe:bebe:bebe:1202:0000:0000:0000:0000/65
                fdbe:bebe:bebe:1203:0000:0000:0000:0000/64
            environment C:
                Nothing
            environment D:
                Nothing
        ##################

        ##################
        Inserting networks:
            - environment B:fdbe:bebe:bebe:1200:0000:0000:0000:0000/64
            - environment C:fdbe:bebe:bebe:1200:0000:0000:0000:0000/65
            - environment C using prefix 24: fdbe:bebe:bebe:1201:0000:0000:0000:0000/64
            - environment A:fdbe:bebe:bebe:1202:8000:0000:0000:0000/65
            - environment A:fdbe:bebe:bebe:1204:0000:0000:0000:0000/65
            - environment B:fdbe:bebe:bebe:1205:0000:0000:0000:0000/64
            - environment A:fdbe:bebe:bebe:1204:8000:0000:0000:0000/65
            - environment D:fdbe:bebe:bebe:1200:0000:0000:0000:0000/64
        ##################

        """

        # Creates networks with octs
        self.create_netv6_with_octs()

        # Creates networks with auto octs and prefix
        self.create_netv6_without_octs()

    def search_all_vlans(self, ids_env):
        search_vlan = {
            'start_record': 0,
            'end_record': 100,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [
                {'ambiente': id_env} for id_env in ids_env
            ]
        }

        url = '/api/v3/vlan/'

        response = self.client.get(
            prepare_url(url, search=search_vlan, fields=['id']),
            HTTP_AUTHORIZATION=self.authorization
        )

        vlans = response.data['vlans']

        ids_vlans = [id_vlan['id'] for id_vlan in vlans]

        return ids_vlans

    def create_netv6_with_octs(self):
        """Creates networks v6 using first vlan."""

        networks = [{
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1201',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 64,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '0000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000',
            'env': 3
        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1202',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 65,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '8000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000',
            'env': 3
        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1203',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 64,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '0000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000',
            'env': 3
        }]

        fields = [
            'block1',
            'block2',
            'block3',
            'block4',
            'block5',
            'block6',
            'block7',
            'block8',
            'prefix',
            'mask1',
            'mask2',
            'mask3',
            'mask4',
            'mask5',
            'mask6',
            'mask7',
            'mask8',
            'vlan'
        ]
        for network_send in networks:

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            del network_send['env']

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]
            network = [{
                'block1': network_send.get('block1'),
                'block2': network_send.get('block2'),
                'block3': network_send.get('block3'),
                'block4': network_send.get('block4'),
                'block5': network_send.get('block5'),
                'block6': network_send.get('block6'),
                'block7': network_send.get('block7'),
                'block8': network_send.get('block8'),
                'prefix': network_send.get('prefix'),
                'vlan': network_send.get('vlan'),
                'network_type': 3,
                'environmentvip': None
            }]

            id_network = self.create_networkv6s(network)[0]['id']

            # Get object created
            url = '/api/v3/networkv6/%s/' % id_network
            url = prepare_url(url, fields=fields)
            response = self.client.get(
                url, HTTP_AUTHORIZATION=self.authorization
            )

            # Verify if object is right
            self.compare_values(
                json.dumps(network_send, sort_keys=True),
                json.dumps(response.data['networks'][0], sort_keys=True)
            )

    def create_networkv6s(self, netv6_dict):
        response = self.client.post(
            '/api/v3/networkv6/',
            data=json.dumps({'networks': netv6_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def create_netv6_without_octs(self):
        networks = [
            {
                'prefix': None,
                'env': 3,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 4,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': 64,
                'env': 4,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 2,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 2,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 3,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 2,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 5,
                'network_type': 3,
                'environmentvip': None
            }
        ]

        expected_networks = [{
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1200',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 64,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '0000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'

        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1200',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 65,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '8000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'

        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1201',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 64,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '0000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'

        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1202',
            'block5': '8000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 65,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '8000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'

        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1204',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 65,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '8000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'

        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1205',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 64,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '0000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'

        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1204',
            'block5': '8000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 65,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '8000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'
        }, {
            'block1': 'fdbe',
            'block2': 'bebe',
            'block3': 'bebe',
            'block4': '1200',
            'block5': '0000',
            'block6': '0000',
            'block7': '0000',
            'block8': '0000',
            'prefix': 64,
            'mask1': 'ffff',
            'mask2': 'ffff',
            'mask3': 'ffff',
            'mask4': 'ffff',
            'mask5': '0000',
            'mask6': '0000',
            'mask7': '0000',
            'mask8': '0000'
        }]

        fields = [
            'block1',
            'block2',
            'block3',
            'block4',
            'block5',
            'block6',
            'block7',
            'block8',
            'prefix',
            'mask1',
            'mask2',
            'mask3',
            'mask4',
            'mask5',
            'mask6',
            'mask7',
            'mask8',
            'vlan',
        ]
        for network_send, expected_network in izip(networks, expected_networks):

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]
            expected_network['vlan'] = ids_vlans[0]

            id_network = self.create_networkv6s([network_send])[0]['id']

            # Get object created
            url = '/api/v3/networkv6/%s/' % id_network
            url = prepare_url(url, fields=fields)
            response = self.client.get(
                url, HTTP_AUTHORIZATION=self.authorization
            )

            # Verify if object is right
            self.compare_values(
                json.dumps(expected_network, sort_keys=True),
                json.dumps(response.data['networks'][0], sort_keys=True)
            )
