"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from rest_framework.test import APITestCase

from networkapi.requisicaovips.models import ServerPool, ServerPoolMember
from networkapi.test import me
from networkapi.usuario.models import Usuario


class PoolsTest(APITestCase):

    def test_list_environment_with_pools(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/list/environment/with/pools/')
        self.assertEqual(type(response.data), type([]))

        self.client.logout()

    def test_list_pools_members(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/list/members/1/')
        self.assertEqual(type(response.data['pool_members']), type([]))

        self.client.logout()

    def test_get_pools_by_pk(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/getbypk/1/')
        self.assertEqual(type(response.data), type({}))

        self.client.logout()

    def test_list_pools_by_environment_vip(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/list/by/environment/vip/1/')
        self.assertEqual(type(response.data), type([]))

        self.client.logout()

    def test_list_pools_by_environment(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/list/by/environment/1/')
        self.assertEqual(type(response.data['pools']), type([]))

        self.client.logout()

    def test_list_request_vip_by_pool(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/get_requisicoes_vip_by_pool/1/')
        self.assertEqual(type(response.data['requisicoes_vip']), type([]))

        self.client.logout()

    def test_list_optionspool_by_environment(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/get_opcoes_pool_by_ambiente/', {'id_environment': 1})
        self.assertEqual(type(response.data['opcoes_pool']), type([]))

        self.client.logout()

    def test_list_equip_by_ip(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/get_equip_by_ip/1/')
        self.assertEqual(type(response.data), type({}))

        self.client.logout()

    def test_list_pools_members_by_server_pool(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/get_all_members/1/')
        self.assertEqual(type(response.data['server_pool_members']), type([]))

        self.client.logout()

    def test_list_healthchecks(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/pools/list_healthchecks/')
        self.assertEqual(type(response.data['healthchecks']), type([]))

        self.client.logout()

    def test_list_pools_by_reqvip(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/pool_list_by_reqvip/', {'id_vip': 1})
        self.assertEqual(type(response.data['pools']), type([]))

        self.client.logout()

    def test_list_pools_by_environment(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/', {'environment_id': 1})
        self.assertEqual(type(response.data['pools']), type([]))

        self.client.logout()

    def test_disable_pools(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/disable/', {'ids': [1]})
        self.assertEqual(response.status_code, 200)

        self.client.logout()

    def test_enable_pools(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/enable/', {'ids': [1]})
        self.assertEqual(response.status_code, 200)

        self.client.logout()

    def test_create_pools(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/create/', {'ids': [1]})
        self.assertEqual(response.status_code, 200)

        sp = ServerPool.objects.get(id=1)
        self.assertEqual(sp.pool_created, True)

        self.client.logout()

    def test_remove_pools(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/remove/', {'ids': [1]})
        self.assertEqual(response.status_code, 200)

        sp = ServerPool.objects.get(id=1)
        self.assertEqual(sp.pool_created, False)

        self.client.logout()

    def test_delete_pools(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/delete/', {'ids': [1]})
        self.assertEqual(response.status_code, 200)

        sp_count = ServerPool.objects.filter(id=1).count()
        self.assertEqual(sp_count, 0)

        self.client.logout()

    @me
    def test_save_reals(self):
        """
        """
        user = Usuario.objects.get(user='TEST')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/pools/save_reals/', json.dumps({"id_server_pool": 1, "id_pool_member": ["1", ""],
                                                               "ip_list_full": [{"id": "1", "ip": ""},
                                                                                {"id": "1", "ip": ""}],
                                                               "priorities": ["0", "0"],
                                                               "ports_reals": [8081, 8080], "nome_equips": ["", ""],
                                                               "id_equips": ["", ""], "weight": ["0", "0"]}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        sp_count = ServerPoolMember.objects.filter(server_pool=1).count()
        self.assertEqual(sp_count, 2)

        self.client.logout()