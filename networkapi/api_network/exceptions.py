from rest_framework.exceptions import APIException
from rest_framework import status


class CannotRemoveDHCPRelayFromActiveNetwork(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Cannot remove DHCPRelay IP from an active network.'

class DHCPRelayNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No DHCPRelayIPv4 found.'

    def __init__(self, version='', id=None):
        self.detail = u'There is no DHCPRelay%s with id = %s.' % (version, id)

class DHCPRelayAlreadyExistsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'DHCPRelayIP with giver parameters already found.'
    def __init__(self, ip_id, network_id):
        self.detail = u'DHCPRelayIP with giver parameters already found (%s, %s).' % (ip_id, network_id)

class EquipmentIDNotInCorrectEnvException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipments are not part of network environment.'

class IncorrectNetworkRouterRegistryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipment IPs not correctly registered. \
             In case of multiple gateways, they should have a registered IP other than the gateway.'

class IncorrectRedundantGatewayRegistryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipment IPs not correctly registered. \
         Equipments should have first IP of network allocated for them as gateways.'

class InvalidInputException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'

class InvalidNetworkIDException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Network ID.'

class NoEnvironmentRoutersFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No environment routers found for network configuration.'



