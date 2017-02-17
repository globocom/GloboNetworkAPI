# -*- coding: utf-8 -*-
import json
import logging
import os
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

    fixtures_base_path = 'networkapi/api_network/fixtures/%s'

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

        fixtures_base_path % 'initial_environment_dc.json',
        fixtures_base_path % 'initial_environment_envlog.json',
        fixtures_base_path % 'initial_environment_gl3.json',
        verbosity=1
    )


class NetworksFunctionalTest2V3(NetworkApiTestCase):

    def setUp(self):

        self.client = Client()

        self.vlan_url_prefix_gen = '/api/v3/vlan/'
        self.vlan_url_prefix_ids = '/api/v3/vlan/%s/'

        self.netv4_url_prefix_gen = '/api/v3/networkv4/'
        self.netv4_url_prefix_ids = '/api/v3/networkv4/%s/'

        self.netv6_url_prefix_gen = '/api/v3/networkv6/'
        self.netv6_url_prefix_ids = '/api/v3/networkv6/%s/'

        self.sufix = time()
        self.configs()
        self.objects = dict()

        self.authorization = self.get_http_authorization('test')

    def tearDown(self):

        pass

    def test_create_networkv4_by_zero(self):
        """
        Test of integration for create environment, vlan, eqpt networks v4.

        ##################
        Starting test:
            - environment A:
                - eqpt 1, 2, 3
                - vrf 1
                - starting vlans 1,2,3
            - environment B:
                - eqpt 2, 4, 5
                - vrf 1
                - starting vlans 4, 5, 6, 7, 8, 9
            - environment C:
                - EQpt 5, 6
                - vrf 2
                - startinG vlans 10, 11
            - environment D:
                - eqpt 7
                - vrf 1
                - starting vlans 1
        ##################

        ##################
        Inserting new vlans without numbers:
            - environment A: Expected 10
            - environment B: Expected 12
            - environment C: Expected 1
            - environment C: Expected 2
            - environment C: Expected 3
            - environment C: Expected 13
            - environment B: Expected 14
            - environment B: Expected 15
            - environment B: Expected 16
            - environment A: Expected 11
            - environment A: Expected 13
            - environment A: Expected 17
            - environment A: Expected 18
            - environment B: Expected 19
            - environment C: Expected 17
            - environment D: Expected 1
        ##################

        ##################
        Starting networks:
            environment A:
                Nothing
            environment B:
                10.0.1.0/24
                10.0.2.0/25
                10.0.3.0/24
            environment C:
                Nothing
            environment D:
                Nothing
        ##################

        ##################
        Inserting networks without octs:
            - environment B: Expected 10.0.0.0/24
            - environment C: Expected 10.0.0.0/25
            - environment C using prefix 24: Expected 10.0.1.0/24
            - environment A: Expected 10.0.2.128/25
            - environment A: Expected 10.0.4.0/25
            - environment B: Expected 10.0.5.0/24
            - environment A: Expected 10.0.4.128/25
            - environment D: Expected 10.0.0.0/24
        ##################

        """

        # Creates VRF 1
        id_vrf_a = self.create_vrf('BeTeste-1')
        self.objects['id_vrf'] = [id_vrf_a]

        # Creates VRF 2
        id_vrf_b = self.create_vrf('BeTeste-2')
        self.objects['id_vrf'].append(id_vrf_b)

        # Creates Environment DC and Logic
        id_envdc = 1
        id_envlog = 1
        self.objects['id_envdc'] = [id_envdc]
        self.objects['id_envlog'] = [id_envlog]

        # Creates environment layer 3 for load balancing
        id_envl3 = 1
        self.objects['id_envl3'] = [id_envl3]

        # Creates environment of load balancing
        id_env = self.create_env(id_envl3, id_envlog, id_envdc,
                                 id_vrf_a, self.configs['env_lb'])
        self.objects['id_envlb'] = [id_env]

        env_list = {'A': id_vrf_a, 'B': id_vrf_a, 'C': id_vrf_b, 'D': id_vrf_a}

        l3_list = {'A': 2, 'B': 3, 'C': 4, 'D': 5}

        # Creates environments of racks
        for i in env_list:
            # Creates environment layer 3 for racks
            id_envl3 = l3_list[i]
            self.objects['id_envl3'].append(id_envl3)

            id_env = self.create_env(id_envl3, id_envlog, id_envdc,
                                     env_list[i], self.configs[i])
            self.objects['id_envrk_' + i] = id_env

        # Creates equipments with relationship environments
        self.create_equipments()

        # Creates vlans with numbers
        self.create_vlans_with_number_envs()

        # Creates vlans with auto numbers
        self.create_vlans_without_number()

        # Creates networks v4 with octs
        self.create_netv4_with_octs()

        # Creates networks with auto octs and prefix
        self.create_netv4_without_octs()

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
        Inserting new vlans:
            - environment A: 10
            - environment B: 12
            - environment C: 1
            - environment C: 2
            - environment C: 3
            - environment C: 13
            - environment B: 14
            - environment B: 15
            - environment B: 16
            - environment A: 11
            - environment A: 13
            - environment A: 17
            - environment A: 18
            - environment B: 19
            - environment C: 17
            - environment D: 1
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

        # Creates VRF 1
        id_vrf_a = self.create_vrf('BeTeste-1')
        self.objects['id_vrf'] = [id_vrf_a]

        # Creates VRF 2
        id_vrf_b = self.create_vrf('BeTeste-2')
        self.objects['id_vrf'].append(id_vrf_b)

        # Creates Environment DC and Logic
        id_envdc = 1
        id_envlog = 1
        self.objects['id_envdc'] = [id_envdc]
        self.objects['id_envlog'] = [id_envlog]

        # Creates environment layer 3 for load balancing
        id_envl3 = 1
        self.objects['id_envl3'] = [id_envl3]

        # Creates environment of load balancing
        id_env = self.create_env(id_envl3, id_envlog, id_envdc,
                                 id_vrf_a, self.configs['env_lb'])
        self.objects['id_envlb'] = [id_env]

        env_list = {'A': id_vrf_a, 'B': id_vrf_a, 'C': id_vrf_b, 'D': id_vrf_a}

        l3_list = {'A': 2, 'B': 3, 'C': 4, 'D': 5}

        # Creates environments of racks
        for i in env_list:
            # Creates environment layer 3 for racks
            id_envl3 = l3_list[i]
            self.objects['id_envl3'].append(id_envl3)

            id_env = self.create_env(id_envl3, id_envlog, id_envdc,
                                     env_list[i], self.configs[i])
            self.objects['id_envrk_' + i] = id_env

        # Creates equipments with relationship environments
        self.create_equipments()

        # Creates vlans with numbers
        self.create_vlans_with_number_envs()

        # Creates vlans with auto numbers
        self.create_vlans_without_number()

        # Creates networks with octs
        self.create_netv6_with_octs()

        # Creates networks with auto octs and prefix
        self.create_netv6_without_octs()

    def configs(self):
        self.configs = {
            'env_lb': [{
                'subnet': 'febe:bebe:bebe:8200:0:0:0:0/57',
                'new_prefix': '64',
                'type': 'v6',
                'network_type': 3
            }, {
                'subnet': '10.10.0.0/16',
                'new_prefix': '24',
                'type': 'v4',
                'network_type': 3
            }],
            'A': [{
                'subnet': 'fdbe:bebe:bebe:1200:0000:0000:0000:0000/57',
                'new_prefix': '65',
                'type': 'v6',
                'network_type': 3
            }, {
                'subnet': '10.0.0.0/16',
                'new_prefix': '25',
                'type': 'v4',
                'network_type': 3
            }],
            'B': [{
                'subnet': 'fdbe:bebe:bebe:1200:0000:0000:0000:0000/57',
                'new_prefix': '64',
                'type': 'v6',
                'network_type': 3
            }, {
                'subnet': '10.0.0.0/16',
                'new_prefix': '24',
                'type': 'v4',
                'network_type': 3
            }],
            'C': [{
                'subnet': 'fdbe:bebe:bebe:1200:0000:0000:0000:0000/57',
                'new_prefix': '65',
                'type': 'v6',
                'network_type': 3
            }, {
                'subnet': '10.0.0.0/16',
                'new_prefix': '25',
                'type': 'v4',
                'network_type': 3
            }],
            'D': [{
                'subnet': 'fdbe:bebe:bebe:1200:0000:0000:0000:0000/57',
                'new_prefix': '64',
                'type': 'v6',
                'network_type': 3
            }, {
                'subnet': '10.0.0.0/16',
                'new_prefix': '24',
                'type': 'v4',
                'network_type': 3
            }]
        }

    def create_vrf(self, name):
        """Creates VRF."""

        vrf_dict = [{
            'internal_name': '%s-%s' % (name, self.sufix),
            'vrf': '%s-%s' % (name, self.sufix)
        }]

        response = self.client.post(
            '/api/v3/vrf/',
            data=json.dumps({'vrfs': vrf_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        id_vrf = response.data[0]['id']

        return id_vrf

    def create_env(self, id_envl3, id_envlog, id_envdc, id_vrf, configs):
        """Creates environment."""

        env_dict = [{
            'grupo_l3': int(id_envl3),
            'ambiente_logico': int(id_envlog),
            'divisao_dc': int(id_envdc),
            'filter': 1,
            'default_vrf': id_vrf,
            'min_num_vlan_1': 1,
            'max_num_vlan_1': 500,
            'min_num_vlan_2': 1000,
            'max_num_vlan_2': 1500,
            'configs': configs,
            'link': 'TEST-LINK'
        }]

        response = self.client.post(
            '/api/v3/environment/',
            data=json.dumps({'environments': env_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        id_env = response.data[0]['id']

        return id_env

    def create_equipments(self):
        """Creates equipments."""

        eqpt_dict = [{
            'name': 'TESTE-EQUIP-1%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_A']
            }]
        }, {
            'name': 'TESTE-EQUIP-2%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_A']
            }]
        }, {
            'name': 'TESTE-EQUIP-3%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_A']
            }, {
                'is_router': False,
                'environment': self.objects['id_envrk_B']
            }]
        }, {
            'name': 'TESTE-EQUIP-4%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_B']
            }]
        }, {
            'name': 'TESTE-EQUIP-5%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_B']
            }, {
                'is_router': False,
                'environment': self.objects['id_envrk_C']
            }]
        }, {
            'name': 'TESTE-EQUIP-6%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_C']
            }]
        }, {
            'name': 'TESTE-EQUIP-7%s' % self.sufix,
            'maintenance': False,
            'equipment_type': 3,
            'model': 1,
            'environments': [{
                'is_router': False,
                'environment': self.objects['id_envrk_D']
            }]
        }]

        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps({'equipments': eqpt_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        ids = response.data
        self.objects['id_eqpt'] = ids

    def create_vlans(self, vlan_dict):
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps({'vlans': vlan_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def get_vlans(self, vlan_ids):

        url = '/api/v3/vlan/%s/' % ';'.join(vlan_ids)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def create_networkipv4s(self, netv4_dict):
        response = self.client.post(
            '/api/v3/networkipv4/',
            data=json.dumps({'networks': netv4_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def get_networkipv4s(self, netv4_ids, **kwargs):

        url = '/api/v3/networkipv4/%s/' % ';'.join(netv4_ids)

        url = prepare_url(url, kwargs)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def create_networkipv6s(self, netv6_dict):
        response = self.client.post(
            '/api/v3/networkipv6/',
            data=json.dumps({'networks': netv6_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def get_networkipv6s(self, netv4_ids, **kwargs):

        url = '/api/v3/networkipv4/%s/' % ';'.join(netv4_ids)

        url = prepare_url(url, kwargs)

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def create_vlans_without_number(self):
        """Creates vlans without number."""

        id_env_a = self.objects['id_envrk_A']
        id_env_b = self.objects['id_envrk_B']
        id_env_c = self.objects['id_envrk_C']
        id_env_d = self.objects['id_envrk_D']

        list_envs_alocate_vlans = [
            id_env_a, id_env_b, id_env_c, id_env_c, id_env_c, id_env_c,
            id_env_b, id_env_b, id_env_b, id_env_a, id_env_a, id_env_a,
            id_env_a, id_env_b, id_env_c, id_env_d
        ]

        list_expected_num_vlans = [
            10, 12, 1, 2, 3, 13, 14, 15, 16, 11, 13, 17, 18, 19, 17, 1
        ]

        vlans = []
        for i, id_env in enumerate(list_envs_alocate_vlans):
            vlan_dict = [{
                'name': 'Vlan auto %s - %s' % (i, self.sufix),
                'environment': id_env,
                'description': 'Test-Description',
                'acl_file_name': 'testaclv4',
                'acl_file_name_v6': 'testaclv6'

            }]

            id_vlan = [str(self.create_vlans(vlan_dict)[0]['id'])]

            vlan_obj = self.get_vlans(id_vlan)['vlans'][0]

            vlans.append(vlan_obj)

        self.verify_num_vlan(vlans, list_expected_num_vlans)

    def create_vlans_with_number(self, nums_vlan, id_env):
        """Creates vlans with number."""

        vlans = []
        for num_vlan in nums_vlan:
            vlan_dict = [{
                'name': 'Vlan %s' % (num_vlan),
                'environment': id_env,
                'num_vlan': num_vlan,
                'description': 'Test-Description',
                'acl_file_name': 'testaclv4',
                'acl_file_name_v6': 'testaclv6'

            }]
            id_vlan = [str(self.create_vlans(vlan_dict)[0]['id'])]
            vlan_obj = self.get_vlans(id_vlan)['vlans'][0]

            vlans.append(vlan_obj)

        return vlans

    def create_vlans_with_number_envs(self):
        """Creates vlans with number for environments A, B and C."""

        id_env_a = self.objects['id_envrk_A']
        id_env_b = self.objects['id_envrk_B']
        id_env_c = self.objects['id_envrk_C']

        # Environment A
        # [1, 2, 3]
        nums_vlan = range(1, 4)
        # Creates Vlans
        id_vlans = self.create_vlans_with_number(nums_vlan, id_env_a)
        ids = [str(id_vlan['id'])for id_vlan in id_vlans]
        # Get Vlans
        vlans = self.get_vlans(ids)['vlans']
        # Verify num vlans was created
        self.verify_num_vlan(vlans, nums_vlan)

        # Environment B
        # [4, 5, 6, 7, 8, 9]
        nums_vlan = range(4, 10)
        # Creates Vlans
        id_vlans = self.create_vlans_with_number(nums_vlan, id_env_b)
        ids = [str(id_vlan['id']) for id_vlan in id_vlans]
        # Get Vlans
        vlans = self.get_vlans(ids)['vlans']
        # Verify num vlans was created
        self.verify_num_vlan(vlans, nums_vlan)

        # Environment C
        # [10, 11]
        nums_vlan = range(10, 12)
        # Creates Vlans
        id_vlans = self.create_vlans_with_number(nums_vlan, id_env_c)
        ids = [str(id_vlan['id']) for id_vlan in id_vlans]
        # Get Vlans
        vlans = self.get_vlans(ids)['vlans']
        # Verify num vlans was created
        self.verify_num_vlan(vlans, nums_vlan)

    def verify_num_vlan(self, objs, nums_vlan):
        for obj, num_vlan in izip(objs, nums_vlan):
            self.assertEqual(
                num_vlan,
                obj.get('num_vlan'),
                'Num vlan should be %s was %s' % (
                    num_vlan, obj.get('num_vlan'))
            )

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

    def create_netv4_with_octs(self):
        """Creates networks v4 using first vlan."""

        networks = [{
            'oct1': 10,
            'oct2': 0,
            'oct3': 1,
            'oct4': 0,
            'prefix': 24,
            'env': self.objects['id_envrk_B']
        }, {
            'oct1': 10,
            'oct2': 0,
            'oct3': 2,
            'oct4': 0,
            'prefix': 25,
            'env': self.objects['id_envrk_B']
        }, {
            'oct1': 10,
            'oct2': 0,
            'oct3': 3,
            'oct4': 0,
            'prefix': 24,
            'env': self.objects['id_envrk_B']
        }]

        fields = [
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'prefix',
            'vlan'
        ]
        for network_send in networks:

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            del network_send['env']

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]
            network = [{
                'oct1': network_send.get('oct1'),
                'oct2': network_send.get('oct2'),
                'oct3': network_send.get('oct3'),
                'oct4': network_send.get('oct4'),
                'prefix': network_send.get('prefix'),
                'vlan': network_send.get('vlan'),
                'network_type': 6,
                'environmentvip': None
            }]

            id_network = self.create_networkipv4s(network)[0]['id']

            # Get object created
            network_rec = self.get_networkipv4s(
                [str(id_network)], fields=fields)['networks'][0]

            # Verify if object is right
            self.assertDictEqual(
                network_send,
                network_rec,
                'Network should be %s and was %s' % (network_send, network_rec)
            )

    def create_netv4_without_octs(self):
        networks = [
            {
                'prefix': None,
                'env': self.objects['id_envrk_B'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_C'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': 24,
                'env': self.objects['id_envrk_C'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_A'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_A'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_B'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_A'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_D'],
                'network_type': 6,
                'environmentvip': None
            }
        ]

        expected_networks = [
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0,
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 0,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128,
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 1,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0,
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 2,
                'oct4': 128,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 4,
                'oct4': 0,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 5,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 4,
                'oct4': 128,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0
            }
        ]

        fields = [
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'prefix',
            'mask_oct1',
            'mask_oct2',
            'mask_oct3',
            'mask_oct4',
        ]
        for network_send, expected_network in izip(networks, expected_networks):

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]

            id_network = self.create_networkipv4s([network_send])[0]['id']

            network_rec = self.get_networkipv4s(
                [str(id_network)], fields=fields)['networks'][0]

            self.assertDictEqual(
                expected_network,
                network_rec,
                'Network should be %s and was %s' % (
                    expected_network, network_rec)
            )

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
            'env': self.objects['id_envrk_B']
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
            'env': self.objects['id_envrk_B']
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
            'env': self.objects['id_envrk_B']
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
                'network_type': 6,
                'environmentvip': None
            }]

            id_network = self.create_networkipv6s(network)[0]['id']

            # Get object created
            network_rec = self.get_networkipv6s(
                [str(id_network)], fields=fields)['networks'][0]

            # Verify if object is right
            self.assertDictEqual(
                network_send,
                network_rec,
                'Network should be %s and was %s' % (network_send, network_rec)
            )

    def create_netv6_without_octs(self):
        networks = [
            {
                'prefix': None,
                'env': self.objects['id_envrk_B'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_C'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': 64,
                'env': self.objects['id_envrk_C'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_A'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_A'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_B'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_A'],
                'network_type': 6,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': self.objects['id_envrk_D'],
                'network_type': 6,
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
            'mask8'
        ]
        for network_send, expected_network in izip(networks, expected_networks):

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]

            id_network = self.create_networkipv6s([network_send])[0]['id']

            network_rec = self.get_networkipv6s(
                [str(id_network)], fields=fields)['networks'][0]

            self.assertDictEqual(
                expected_network,
                network_rec,
                'Network should be %s and was %s' % (
                    expected_network, network_rec)
            )
