# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import unittest
from django.core.exceptions import ObjectDoesNotExist
from mock import patch, MagicMock
from rest_framework.test import APIClient
from networkapi.ambiente.models import Ambiente, EnvironmentVip, DivisaoDc, AmbienteLogico, GrupoL3
from networkapi.api_pools.exceptions import *
from networkapi.api_pools.models import OptionPool
from networkapi.api_rest.exceptions import EnvironmentEnvironmentVipNotBoundedException
from networkapi.equipamento.models import Equipamento
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.ip.models import Ip
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember
from networkapi.test import mock_login, load_json

class PoolSaveTestCase(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()
        self.mock_get_environment_by_id(Ambiente(id = 1))

    def tearDown(self):
        pass

    @mock_login
    def test_save_pool_given_no_service_down_action_available(self):
        self.mock_get_service_down_action_by_environment(None)

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals("Invalid value for Service-Down-Action.", response.data.get('detail'))

    @mock_login
    def test_save_pool_given_duplicate_identifier(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(ServerPool(identifier = "pool_1"))

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals("Identifier already exists.", response.data.get('detail'))

    @mock_login
    def test_save_pool_given_invalid_service_down_action_id(self):
        self.mock_get_service_down_action_by_pk(None)

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool_with_service_down_action.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals("Invalid value for Service-Down-Action.", response.data.get('detail'))

    @mock_login
    def test_save_pool_given_invalid_identifier(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool_with_invalid_identifier.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals("The first character of the identifier field can not be a number.", response.data.get('detail'))

    @mock_login
    def test_save_pool_given_invalid_health_check(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool_with_invalid_health_check.json'), format='json')
        self.assertEquals(500, response.status_code)
        self.assertEquals("Failed to access the data source.", response.data.get('detail'))

    @mock_login
    def test_save_pool_given_pool_already_created_on_equipment(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(UpdateEnvironmentPoolCreatedException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Ambiente nao pode ser alterado pois o server pool ja esta criado no equipamento.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_pool_associated_with_one_or_more_vips(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(UpdateEnvironmentVIPException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Ambiente nao pode ser alterado pois o server pool esta associado com um ou mais VIP.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_pool_associated_with_one_or_more_pool_members(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(UpdateEnvironmentServerPoolMemberException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Ambiente nao pode ser alterado pois o server pool esta associado com um ou mais server pool member.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_pool_already_having_an_identifier_saved(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(CreatedPoolIdentifierException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Pool already created. Cannot change Identifier.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_fail_on_change_pool_limits(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(ScriptAlterLimitPoolDiffMembersException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Failed to change limits for pool. Members limit differs from pool default limit     Set all members with the same default limit before changing default pool limit.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_fail_on_execute_limit_script_for_pool(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(ScriptAlterLimitPoolException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Failed to execute limits script for pool.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_fail_on_execute_create_pool_script(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(ScriptCreatePoolException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Failed to execute create script for pool.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_fail_on_create_service_down_action(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool(ScriptAlterServiceDownActionException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Failed to execute service-down-action script for pool.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)

    @mock_login
    def test_save_pool_given_invalid_real_data(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool((self.create_server_pool_model(), None))
        prepare_to_save_reals_mock = self.mock_prepare_to_save_reals(InvalidRealPoolException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Parametros invalidos do real.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)
        self.assertTrue(prepare_to_save_reals_mock.called)

    @mock_login
    def test_save_pool_given_environment_not_linked_to_vip_environment(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool((self.create_server_pool_model(), None))
        prepare_to_save_reals_mock = self.mock_prepare_to_save_reals([self.create_real_dict()])
        reals_can_associate_server_pool_mock = self.mock_reals_can_associate_server_pool(EnvironmentEnvironmentVipNotBoundedException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('There is no link between environment and environment vip.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)
        self.assertTrue(prepare_to_save_reals_mock.called)
        self.assertTrue(reals_can_associate_server_pool_mock.called)


    @mock_login
    def test_reals_can_associate_server_pool_given_environment_not_linked_to_vip_environment(self):
        #imported locally given conflict in namespace
        from networkapi.api_pools.views import reals_can_associate_server_pool

        self.mock_get_environment_vips_by_environment_id(EnvironmentVip(id = 1, finalidade_txt = 'environment_1'))
        self.mock_get_environment_list_by_environment_vip_list([])
        self.mock_get_ip_by_ok(self.create_ipv4())
        self.mock_find_environment_by_id(self.create_environment())

        with self.assertRaises(EnvironmentEnvironmentVipNotBoundedException):
            reals_can_associate_server_pool(self.create_server_pool_model(), [self.create_real_dict()])

    @mock_login
    def test_reals_can_associate_server_pool_given_environment_linked_to_vip_environment(self):
        #imported locally given conflict in namespace
        from networkapi.api_pools.views import reals_can_associate_server_pool

        self.mock_get_environment_vips_by_environment_id(EnvironmentVip(id = 1, finalidade_txt = 'environment_1'))
        self.mock_get_environment_list_by_environment_vip_list([self.create_environment()])
        self.mock_get_ip_by_ok(self.create_ipv4())
        self.mock_find_environment_by_id(self.create_environment())

        reals_can_associate_server_pool(self.create_server_pool_model(), [self.create_real_dict()])

    @mock_login
    def test_save_pool_given_script_error_on_save_pool(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool((self.create_server_pool_model(), None))
        prepare_to_save_reals_mock = self.mock_prepare_to_save_reals([self.create_real_dict()])
        reals_can_associate_server_pool_mock = self.mock_reals_can_associate_server_pool(None)
        save_server_pool_member_mock = self.mock_save_server_pool_member(ScriptCreatePoolException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Failed to execute create script for pool.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)
        self.assertTrue(prepare_to_save_reals_mock.called)
        self.assertTrue(reals_can_associate_server_pool_mock.called)
        self.assertTrue(save_server_pool_member_mock.called)

    @mock_login
    def test_save_pool_given_script_error_change_pool_priority(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool((self.create_server_pool_model(), None))
        prepare_to_save_reals_mock = self.mock_prepare_to_save_reals([self.create_real_dict()])
        reals_can_associate_server_pool_mock = self.mock_reals_can_associate_server_pool(None)
        save_server_pool_member_mock = self.mock_save_server_pool_member(ScriptAlterPriorityPoolMembersException())

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(400, response.status_code)
        self.assertEquals('Failed to execute priority script for pool.', response.data.get('detail'))
        self.assertTrue(save_pool_mock.called)
        self.assertTrue(prepare_to_save_reals_mock.called)
        self.assertTrue(reals_can_associate_server_pool_mock.called)
        self.assertTrue(save_server_pool_member_mock.called)

    @mock_login
    def test_save_pool_given_(self):
        self.mock_get_service_down_action_by_environment(OptionPool(name = 'none'))
        self.mock_filter_server_pool_by_identifier(None)
        self.mock_get_or_create_healthcheck(Healthcheck())
        save_pool_mock = self.mock_save_server_pool((self.create_server_pool_model(), None))
        prepare_to_save_reals_mock = self.mock_prepare_to_save_reals([self.create_real_dict()])
        reals_can_associate_server_pool_mock = self.mock_reals_can_associate_server_pool(None)
        save_server_pool_member_mock = self.mock_save_server_pool_member([self.create_pool_member()])

        response = self.client.post('/api/pools/save/', self.load_pool_json('pool.json'), format='json')
        self.assertEquals(201, response.status_code)
        self.assertEquals("pool_1", response.data.get("server_pool").get("identifier"))
        self.assertEquals(8080, response.data.get("server_pool").get("default_port"))
        self.assertEquals(1, len(response.data.get("server_pool_members")))
        self.assertTrue(save_pool_mock.called)
        self.assertTrue(prepare_to_save_reals_mock.called)
        self.assertTrue(reals_can_associate_server_pool_mock.called)
        self.assertTrue(save_server_pool_member_mock.called)

#UTILS
    def create_pool_member(self):
        pool = self.create_server_pool_model()
        member = ServerPoolMember(
            server_pool=pool,
            identifier='member_1',
            ip=self.create_ipv4(),
            priority=1,
            weight=0,
            limit=pool.default_limit,
            port_real=8080
        )
        member.equipment = Equipamento(id = 1, nome = "l-59c0df40-624d-4174-ad7e-a67e54bb3ced")
        return member

    def create_real_dict(self):
        return {
            'id': 1,
            'ip': '10.170.0.4',
            'port_real': 8080,
            'nome_equips': 'l-59c0df40-624d-4174-ad7e-a67e54bb3ced',
            'priority': 0,
            'weight': 0,
            'id_pool_member': 0
        }

    def create_ipv4(self):
        return Ip(oct1=10, oct2=170, oct3=0, oct4=4)

    def create_server_pool_model(self):
        return ServerPool(
            id = 1,
            default_port = 8080,
            identifier = "pool_1",
            environment = Ambiente(id = 1)
        )

    def create_environment(self):
        return Ambiente(divisao_dc=DivisaoDc(nome='division_1'), ambiente_logico=AmbienteLogico(nome='env'), grupo_l3 = GrupoL3(nome='l3'))
    
    def load_pool_json(self, file_name):
        path = os.path.dirname(os.path.realpath(__file__)) + '/' + file_name
        return load_json(path)

    #MOCKS
    def mock_get_service_down_action_by_environment(self, option_pool):
        mock = patch("networkapi.api_pools.models.OptionPool.get_all_by_type_and_environment").start()
        query_return_mock = MagicMock()
        if option_pool is None:
            query_return_mock.get.side_effect = ObjectDoesNotExist()
        else:
            query_return_mock.get.return_value = option_pool
        mock.return_value = query_return_mock

    def mock_get_service_down_action_by_pk(self, option_pool):
        mock = patch("networkapi.api_pools.models.OptionPool.get_by_pk").start()
        if option_pool is None:
            mock.side_effect = ObjectDoesNotExist()
        else:
            mock.return_value = option_pool

    def mock_filter_server_pool_by_identifier(self, server_pool):
        mock = patch("networkapi.requisicaovips.models.ServerPool.objects.filter").start()
        mock.return_value = MagicMock()
        mock.return_value.count = lambda : 1 if server_pool is not None else 0

    def mock_get_or_create_healthcheck(self, healthcheck):
        mock = patch("networkapi.api_pools.views.get_or_create_healthcheck").start()
        mock.return_value = healthcheck

    def mock_get_environment_by_id(self, environment):
        mock = patch("networkapi.ambiente.models.Ambiente.objects.get").start()
        mock.return_value = environment

    def mock_save_server_pool(self, response):
        mock = patch("networkapi.api_pools.views.save_server_pool").start()
        if(issubclass(response.__class__, Exception)):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock

    def mock_prepare_to_save_reals(self, response):
        mock = patch("networkapi.api_pools.views.prepare_to_save_reals").start()
        if(issubclass(response.__class__, Exception)):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock

    def mock_reals_can_associate_server_pool(self, response):
        mock = patch("networkapi.api_pools.views.reals_can_associate_server_pool").start()
        if(issubclass(response.__class__, Exception)):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock

    def mock_get_environment_list_by_environment_vip_list(self, related_environments):
        patch(
            'networkapi.ambiente.models.EnvironmentEnvironmentVip.get_environment_list_by_environment_vip_list'
        ).start().return_value = related_environments

    def mock_get_environment_vips_by_environment_id(self, vip_environment):
        patch(
            'networkapi.ambiente.models.EnvironmentVip.get_environment_vips_by_environment_id'
        ).start().return_value = [vip_environment]

    def mock_find_environment_by_id(self, environment):
        mock = patch('networkapi.ambiente.models.Ambiente.objects.filter').start()
        mock.return_value = MagicMock()
        mock.return_value.uniqueResult.return_value = environment

    def mock_get_ip_by_ok(self, ip):
        patch('networkapi.ip.models.Ip.get_by_pk').start().return_value = ip

    def mock_save_server_pool_member(self, response):
        mock = patch("networkapi.api_pools.views.save_server_pool_member").start()
        if(issubclass(response.__class__, Exception)):
            mock.side_effect = response
        else:
            mock.return_value = response
        return mock