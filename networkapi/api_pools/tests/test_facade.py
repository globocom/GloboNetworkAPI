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

class PoolFacadeTestCase(unittest.TestCase):

    def setUp(self):
        self.user = Usuario(id = 1, nome = 'users')
        self.mock_transaction()

    def tearDown(self):
        patch.stopall()

    def test_get_healthcheck_given_invalid_healthcheck_identifier(self):
        find_health_check_mock = self.mock_find_healthcheck(ObjectDoesNotExist())
        save_health_check_mock = self.mock_healthcheck_save()
        health_check = get_or_create_healthcheck(self.user, 'WORKING', 'HTTP', '/healthcheck', '*:*', '1')

        self.assertEquals('WORKING', health_check.healthcheck_expect)
        self.assertEquals('HTTP', health_check.healthcheck_type)
        self.assertEquals('/healthcheck', health_check.healthcheck_request)
        self.assertEquals('*:*', health_check.destination)
        self.assertEquals('1', health_check.identifier)
        self.assertIsNotNone(health_check)
        self.assertTrue(find_health_check_mock.called)
        self.assertTrue(save_health_check_mock.called)

    def test_get_healthcheck_given_multiple_healthchecK_found(self):
        healthcheck = self.create_health_check(expect='WORKING', type='HTTP', req='/healthcheck', dest='*:*', ident='1')
        find_health_check_mock = self.mock_find_healthcheck(MultipleObjectsReturned())
        filter_health_check_mock = self.mock_healthcheck_filter([healthcheck])
        health_check = get_or_create_healthcheck(self.user, 'WORKING', 'HTTP', '/healthcheck', '*:*', '1')

        self.assertEquals('WORKING', health_check.healthcheck_expect)
        self.assertEquals('HTTP', health_check.healthcheck_type)
        self.assertEquals('/healthcheck', health_check.healthcheck_request)
        self.assertEquals('*:*', health_check.destination)
        self.assertEquals('1', health_check.identifier)
        self.assertIsNotNone(health_check)
        self.assertTrue(find_health_check_mock.called)
        self.assertTrue(filter_health_check_mock.called)

    def test_create_new_healthcheck(self):
        find_health_check_mock = self.mock_find_healthcheck(ObjectDoesNotExist())
        save_health_check_mock = self.mock_healthcheck_save()
        health_check = get_or_create_healthcheck(self.user, 'WORKING', 'HTTP', '/healthcheck', '*:*')

        self.assertEquals('WORKING', health_check.healthcheck_expect)
        self.assertEquals('HTTP', health_check.healthcheck_type)
        self.assertEquals('/healthcheck', health_check.healthcheck_request)
        self.assertEquals('*:*', health_check.destination)
        self.assertEquals('', health_check.identifier)
        self.assertIsNotNone(health_check)
        self.assertTrue(find_health_check_mock.called)
        self.assertTrue(save_health_check_mock.called)

    def test_is_valid_healthcheck_destination(self):
        self.assertTrue(is_valid_healthcheck_destination("*:*"))
        self.assertTrue(is_valid_healthcheck_destination("80:*"))
        self.assertTrue(is_valid_healthcheck_destination("*:80"))
        self.assertTrue(is_valid_healthcheck_destination("80:8080"))
        self.assertIsNone(is_valid_healthcheck_destination("*:192.168.10.1"))

    def test_update_pool_fields(self):
        pool = ServerPool()
        default_port = 8080
        env = Ambiente(id = 1)
        identifier = 'pool_1'
        old_healthcheck = Healthcheck()
        old_lb_method = 'round-robin'
        old_maxconn = 50

        save_pool_mock = self.mock_save_pool()
        update_pool_fields(default_port, env, identifier, old_healthcheck, old_lb_method, old_maxconn, pool, self.user)

        save_pool_mock.assert_calls(call(), call())
        self.assertEquals(default_port, pool.default_port)
        self.assertEquals(env, pool.environment)
        self.assertEquals(identifier, pool.identifier)
        self.assertEquals(old_healthcheck, pool.healthcheck)
        self.assertEquals(old_lb_method, pool.lb_method)

    def test_validate_change_of_environment_given_already_created_pool(self):
        pool = self.mock_server_pool(created = True)
        with self.assertRaises(UpdateEnvironmentPoolCreatedException):
            validate_change_of_environment(1, pool)

    def test_validate_change_of_environment_given_pool_associated_to_vip(self):
        pool = self.mock_server_pool(created = False)
        pool.vipporttopool_set.count = lambda : 1

        with self.assertRaises(UpdateEnvironmentVIPException):
            validate_change_of_environment(1, pool)

    def test_validate_change_of_environment_given_pool_associated_to_one_or_more_pool_members(self):
        pool = self.mock_server_pool(created = False)
        pool.serverpoolmember_set.exclude = lambda id__in : [ServerPoolMember()]
        pool.vipporttopool_set.count = lambda : 0

        with self.assertRaises(UpdateEnvironmentServerPoolMemberException):
            validate_change_of_environment(1, pool)

    def test_validate_change_of_environment_given_pool_not_associated_to_vip_or_members(self):
        pool = self.mock_server_pool(created = False)
        pool.serverpoolmember_set.exclude = lambda id__in : []
        pool.vipporttopool_set.count = lambda : 0

        validate_change_of_environment(1, pool)

    def test_update_maxconn_given_not_created_pool(self):
        exec_script_mock = self.mock_exec_script(0)
        pool = self.mock_server_pool(maxconn = 200)
        new_max_conn = 500
        update_pool_maxconn(new_max_conn, pool.default_limit, pool, self.user)

        self.assertEqual(new_max_conn, pool.default_limit)
        self.assertFalse(exec_script_mock.called)

    def test_update_maxconn_given_created_pool_and_no_members(self):
        exec_script_mock = self.mock_exec_script(0)
        pool = self.mock_server_pool(maxconn = 200, created = True)
        new_max_conn = 500
        update_pool_maxconn(new_max_conn, 300, pool, self.user)

        self.assertEquals(new_max_conn, pool.default_limit)
        self.assertFalse(exec_script_mock.called)

    def test_update_maxconn_given_created_pool_and_having_members(self):
        exec_script_mock = self.mock_exec_script(0)
        member = self.mock_pool_member(maxconn = 300)
        pool = self.mock_server_pool(maxconn = 200, created = True, members = [member])
        new_max_conn = 500
        update_pool_maxconn(new_max_conn, 300, pool, self.user)

        self.assertTrue(exec_script_mock.called)
        self.assertEquals(new_max_conn, pool.default_limit)
        self.assertEquals(new_max_conn, member.limit)

    def test_update_maxconn_given_invalid_script_output(self):
        exec_script_mock = self.mock_exec_script(1)
        member = self.mock_pool_member(maxconn = 300)
        pool = self.mock_server_pool(maxconn = 200, created = True, members = [member])
        new_max_conn = 500

        with self.assertRaises(ScriptAlterLimitPoolException):
            update_pool_maxconn(new_max_conn, 300, pool, self.user)

            self.assertTrue(exec_script_mock.called)
            self.assertNotEquals(new_max_conn, pool.default_limit)
            self.assertNotEquals(new_max_conn, member.limit)

    def test_update_maxconn_given_members_limit_differs_from_pools(self):
        member = self.mock_pool_member(maxconn = 0)
        pool = self.mock_server_pool(maxconn = 200, created = True, members = [member])
        new_max_conn = 500

        with self.assertRaises(ScriptAlterLimitPoolDiffMembersException):
            update_pool_maxconn(new_max_conn, 300, pool, self.user)
            self.assertNotEquals(new_max_conn, pool.default_limit)
            self.assertNotEquals(new_max_conn, member.limit)

    def test_apply_health_check_given_pool_not_created(self):
        pool = self.mock_server_pool(created=False)
        pool.healthcheck = self.create_health_check(id = 1)
        new_healtcheck = self.create_health_check(id = 2)
        script_exec_mock = self.mock_exec_script(1)

        apply_health_check(new_healtcheck, pool.healthcheck, pool, self.user)
        self.assertEquals(new_healtcheck, pool.healthcheck)
        self.assertFalse(script_exec_mock.called)

    def test_apply_health_check_given_created_pool(self):
        pool = self.mock_server_pool(created=True)
        pool.healthcheck = self.create_health_check(id = 1)
        new_healtcheck = self.create_health_check(id = 2)
        script_exec_mock = self.mock_exec_script(0)

        apply_health_check(new_healtcheck, pool.healthcheck, pool, self.user)
        self.assertEquals(new_healtcheck, pool.healthcheck)
        self.assertTrue(script_exec_mock.called)

    def test_apply_health_check_given_script_error_output(self):
        pool = self.mock_server_pool(created=True)
        pool.healthcheck = self.create_health_check(id = 1)
        new_healtcheck = self.create_health_check(id = 2)
        script_exec_mock = self.mock_exec_script(1)

        with self.assertRaises(ScriptCreatePoolException):
            apply_health_check(new_healtcheck, pool.healthcheck, pool, self.user)
            self.assertNotEquals(new_healtcheck, pool.healthcheck)
            self.assertTrue(script_exec_mock.called)

    def test_apply_service_down_action_given_not_created_pool(self):
        pool = self.mock_server_pool(created=False)
        pool.servicedownaction = OptionPool(id = 1, type='ServiceDownAction', name='none')
        new_servicedownaction = OptionPool(id = 2, type='ServiceDownAction', name='drop')
        script_exec_mock = self.mock_exec_script(1)

        apply_service_down_action(pool.servicedownaction, new_servicedownaction, pool, self.user)
        self.assertEquals(new_servicedownaction, pool.servicedownaction)
        self.assertFalse(script_exec_mock.called)

    def test_apply_service_down_action_given_created_pool(self):
        pool = self.mock_server_pool(created=True)
        pool.servicedownaction = OptionPool(id = 1, type='ServiceDownAction', name='none')
        new_servicedownaction = OptionPool(id = 2, type='ServiceDownAction', name='drop')
        script_exec_mock = self.mock_exec_script(0)

        apply_service_down_action(pool.servicedownaction, new_servicedownaction, pool, self.user)
        self.assertEquals(new_servicedownaction, pool.servicedownaction)
        self.assertTrue(script_exec_mock.called)

    def test_apply_service_down_action_given_script_error_output(self):
        pool = self.mock_server_pool(created=True)
        pool.servicedownaction = OptionPool(id = 1, type='ServiceDownAction', name='none')
        new_servicedownaction = OptionPool(id = 2, type='ServiceDownAction', name='drop')
        script_exec_mock = self.mock_exec_script(1)

        with self.assertRaises(ScriptAlterServiceDownActionException):
            apply_service_down_action(pool.servicedownaction, new_servicedownaction, pool, self.user)
            self.assertNotEquals(new_servicedownaction, pool.servicedownaction)
            self.assertTrue(script_exec_mock.called)

    def test_update_load_balancing_method_given_not_created_pool(self):
        pool = self.mock_server_pool(created=False)
        pool.lb_method = 'leastconn'
        new_lb_method = 'round-robin'
        script_exec_mock = self.mock_exec_script(1)

        update_load_balancing_method(new_lb_method, pool.lb_method, pool, self.user)
        self.assertEquals(new_lb_method, pool.lb_method)
        self.assertFalse(script_exec_mock.called)

    def test_update_load_balancing_method_given_created_pool(self):
        pool = self.mock_server_pool(created=True)
        pool.lb_method = 'leastconn'
        new_lb_method = 'round-robin'
        script_exec_mock = self.mock_exec_script(0)

        update_load_balancing_method(new_lb_method, pool.lb_method, pool, self.user)
        self.assertEquals(new_lb_method, pool.lb_method)
        self.assertTrue(script_exec_mock.called)

    def test_update_load_balancing_method_given_script_error_output(self):
        pool = self.mock_server_pool(created=True)
        pool.lb_method = 'leastconn'
        new_lb_method = 'round-robin'
        script_exec_mock = self.mock_exec_script(1)

        with self.assertRaises(ScriptCreatePoolException):
            update_load_balancing_method(new_lb_method, pool.lb_method, pool, self.user)
            self.assertNotEquals(new_lb_method, pool.lb_method)
            self.assertTrue(script_exec_mock.called)

    def test_prepare_to_save_reals_given_invalid_priority(self):
        priorities = [9999999999999999]
        try:
            prepare_to_save_reals([''], [], [], priorities, [], [1], [])
            self.fail()
        except InvalidRealPoolException, e:
            self.assertEquals("Parametros invalidos do real: <<O valor da Prioridade deve estar entre 0 e 4294967295.>>", e.detail)

    def test_prepare_to_save_reals_given_invalid_port(self):
        priorities = [1]
        ports = [999999999]
        try:
            prepare_to_save_reals([''], ports, [], priorities, [], [1], [])
            self.fail()
        except InvalidRealPoolException, e:
            self.assertEquals("Parametros invalidos do real: <<O número da porta deve estar entre 1 e 65535.>>", e.detail)

    def test_prepare_to_save_reals_given_port_count_differs_from_equipment_count(self):
        priorities = [1, 1]
        ports = [8080, 8080]
        pool_member_ids = [1, 2]
        id_equips = [1]
        try:
            prepare_to_save_reals([], ports, [], priorities, [], pool_member_ids, id_equips)
            self.fail()
        except InvalidRealPoolException, e:
            self.assertEquals("Parametros invalidos do real: <<Quantidade de portas e equipamento difere.>>", e.detail)

    def test_prepare_to_save_reals_given_different_ips_with_matching_ports(self):
        priorities = [1, 1]
        ports = [8080, 8080]
        ips = [{'id': 1, 'ip': '192.160.0.1'} ,{'id': 1, 'ip': '192.160.0.1'}]
        pool_member_ids = [1, 2]
        id_equips = [1, 2]
        try:
            prepare_to_save_reals(ips, ports, [], priorities, [], pool_member_ids, id_equips)
            self.fail()
        except InvalidRealPoolException, e:
            self.assertEquals("Parametros invalidos do real: <<Ips com portas iguais.>>", e.detail)

    def test_prepare_to_save_reals_given_valid_parameter_combination(self):
        priorities = [1, 1]
        ports = [8080, 8080]
        ips = [{'id': 1, 'ip': '192.160.0.1'} ,{'id': 2, 'ip': '192.160.0.2'}]
        pool_member_ids = [1, 2]
        id_equips = [1, 2]
        equip_names = ['equip_1', 'equip_2']
        weights = [1, 1]

        reals = prepare_to_save_reals(ips, ports, equip_names, priorities, weights, pool_member_ids, id_equips)

        self.assertEquals(2, len(reals))
        self.assertEquals(1, reals[0].get('id'))
        self.assertEquals('192.160.0.1', reals[0].get('ip'))
        self.assertEquals(8080, reals[0].get('port_real'))
        self.assertEquals('equip_1', reals[0].get('nome_equips'))
        self.assertEquals(1, reals[0].get('priority'))
        self.assertEquals(1, reals[0].get('weight'))
        self.assertEquals(1, reals[0].get('id_pool_member'))

    def test_update_pool_member(self):
        save_member_mock = patch('networkapi.requisicaovips.models.ServerPoolMember.save').start()

        pool = ServerPool(id = 1, default_limit= 1)
        pool_member = ServerPoolMember()
        dict = {'nome_equips': 'equip_name', 'weight': 1, 'priority': 1, 'port_real': 80}
        ip = Ip(id = 1)
        ipv6 = Ipv6(id = 1)
        update_pool_member(pool, pool_member, dict, ip, ipv6, self.user)

        self.assertEquals(pool, pool_member.server_pool)
        self.assertEquals(1, pool_member.limit)
        self.assertEquals(ip, pool_member.ip)
        self.assertEquals(ipv6, pool_member.ipv6)
        self.assertEquals('equip_name', pool_member.identifier)
        self.assertEquals(1, pool_member.weight)
        self.assertEquals(1, pool_member.priority)
        self.assertEquals(80, pool_member.port_real)
        self.assertTrue(save_member_mock.called)

    def test_get_ipv4(self):
        get_by_pk_mock = patch('networkapi.ip.models.Ip.get_by_pk').start()
        get_by_pk_mock.return_value = Ip()

        ip = get_ip_objects({'ip': '192.168.10.2', 'id': 1})

        self.assertTrue(isinstance(ip[0], Ip))
        self.assertIsNone(ip[1])

    def test_get_ipv6(self):
        get_by_pk_mock = patch('networkapi.ip.models.Ipv6.get_by_pk').start()
        get_by_pk_mock.return_value = Ipv6()

        ip = get_ip_objects({'ip': '2001:0db8:85a3:08d3:1319:8a2e:0370:7344', 'id': 1})

        self.assertTrue(isinstance(ip[1], Ipv6))
        self.assertIsNone(ip[0])

    def test_get_pool_members_to_be_removed(self):
        list_server_pool_member = [{'id_pool_member': 1}, {'id_pool_member': ''}]
        self.assertEquals(1, len(get_pool_members_to_be_removed(list_server_pool_member)))

    def test_remove_pool_members_given_no_members_to_be_removed(self):
        exec_script_mock = self.mock_exec_script(0)
        pool = self.mock_server_pool()
        pool.serverpoolmember_set = Mock(exclude = lambda id__in: None)

        remove_pool_members([], pool, self.user)
        self.assertFalse(exec_script_mock.called)

    def test_remove_pool_members_given_not_created_pool(self):
        exec_script_mock = self.mock_exec_script(0)
        pool = self.mock_server_pool(created=False)
        member = self.mock_pool_member()
        pool.serverpoolmember_set = Mock(exclude = lambda id__in: [member])

        remove_pool_members([], pool, self.user)
        self.assertTrue(member.delete.called)
        self.assertFalse(exec_script_mock.called)

    def test_remove_pool_members_given_script_errorl(self):
        exec_script_mock = self.mock_exec_script(1)
        pool = self.mock_server_pool(created=True)
        member = self.mock_pool_member()
        pool.serverpoolmember_set = Mock(exclude = lambda id__in: [member])

        with self.assertRaises(ScriptCreatePoolException):
            remove_pool_members([], pool, self.user)
            self.assertTrue(member.delete.called)
            self.assertTrue(exec_script_mock.called)

    def test_remove_pool_members_given_created_pool(self):
        exec_script_mock = self.mock_exec_script(0)
        pool = self.mock_server_pool(created=True)
        member = self.mock_pool_member()
        pool.serverpoolmember_set = Mock(exclude = lambda id__in: [member])

        remove_pool_members([], pool, self.user)
        self.assertTrue(member.delete.called)
        self.assertTrue(exec_script_mock.called)

    def test_deploy_pool_member_config_given_script_error(self):
        exec_script_mock = self.mock_exec_script(1)
        pool_member = self.mock_pool_member()

        with self.assertRaises(ScriptCreatePoolException):
            deploy_pool_member_config(1, 1, 8080, pool_member, self.user)
            self.assertTrue(pool_member.delete.called)
            self.assertTrue(exec_script_mock.called)

    def test_deploy_pool_member_config(self):
        exec_script_mock = self.mock_exec_script(0)
        pool_member = self.mock_pool_member()

        deploy_pool_member_config(1, 1, 8080, pool_member, self.user)
        self.assertTrue(exec_script_mock.called)
        self.assertFalse(pool_member.delete.called)

    def test_apply_priorities(self):
        exec_script_mock = self.mock_exec_script(0)
        pool_members = [self.mock_pool_member()]
        pool = self.mock_server_pool()

        apply_priorities(pool_members, [1], pool, self.user)
        self.assertTrue(exec_script_mock.called)

    def test_apply_priorities_given_script_error_output(self):
        exec_script_mock = self.mock_exec_script(1)
        pool_members = [self.mock_pool_member()]
        pool = self.mock_server_pool()

        with self.assertRaises(ScriptAlterPriorityPoolMembersException):
            apply_priorities(pool_members, [10], pool, self.user)
            self.assertEquals(10, pool_members[0].priority)
            self.assertTrue(pool_members[0].save.called)
            self.assertTrue(exec_script_mock.called)

    #UTILS
    def create_health_check(self, id=0, expect='WORKING', type='HTTP', req='/healthcheck', dest='*:*', ident='1'):
        return Healthcheck(id=id,healthcheck_expect=expect,healthcheck_type=type,healthcheck_request=req,destination=dest,identifier=ident)

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

    def mock_healthcheck_filter(self, healthchecks):
        mock = patch("networkapi.healthcheckexpect.models.Healthcheck.objects.filter").start()
        mock.return_value = Mock()
        mock.return_value.order_by =  lambda field: healthchecks
        return mock

    def mock_save_pool(self):
        return patch("networkapi.requisicaovips.models.ServerPool.save").start()

    def mock_exec_script(self, script_output):
        exec_script_mock = patch('networkapi.api_pools.facade.facade_v1.exec_script').start()
        exec_script_mock.return_value = (script_output, None, None)
        return exec_script_mock

    def mock_server_pool(self, maxconn = 0, created = False, members = []):
        return Mock(default_limit = maxconn, pool_created = created, serverpoolmember_set = Mock(all = lambda :members), save = lambda : None)

    def mock_pool_member(self, maxconn = 0):
        return MagicMock(save = lambda: None, limit = maxconn)

    def mock_transaction(self):
        patch('networkapi.api_pools.facade.transaction').start()