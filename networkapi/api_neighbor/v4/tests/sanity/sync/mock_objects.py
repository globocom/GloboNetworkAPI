from mock import Mock
from mock import MagicMock
from random import randint

def _mock_equipment():
    equipment = Mock()
    marca = MagicMock(nome='DELL')
    equipment.modelo = MagicMock(nome='FTOS', marca=marca)
    equipment.maintenance = False
    equipment.id = randint(0, 100000)

    return equipment


def _mock_vrf():
    vrf = Mock()
    vrf.id = 1
    vrf.vrf = 'default'
    vrf.internal_name = 'default'

    return vrf

def _mock_asn():
    asn = Mock()
    asn.id = 1
    asn.name = '640404'
    asn.description = 'ASN_640404'

    return asn
