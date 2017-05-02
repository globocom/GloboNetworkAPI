# -*- coding: utf-8 -*-

from django.test.client import Client
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.SDN.ODL.Generic import ODLPlugin
from networkapi.test.test_case import NetworkApiTestCase


class GenericOpenDayLightTestCase(NetworkApiTestCase):
    """ Class for testing the generic OpenDayLight plugin """

    def setUp(self):
        self.client = Client()
        self.equipment = Equipamento(id=1)
        self.equipment_access = EquipamentoAcesso(id=1)

    def test_add_simple_acl_flow(self):
        """ Adding simple ACL flow through generic ODL plugin """

        odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )
        # odl.add_flow({})
