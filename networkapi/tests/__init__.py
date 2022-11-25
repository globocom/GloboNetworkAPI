# Tests for IPV4
from ..api_ip.tests.sanity.ipv4.sync.test_delete import *
from ..api_ip.tests.sanity.ipv4.sync.test_get import *
from ..api_ip.tests.sanity.ipv4.sync.test_post import *
from ..api_ip.tests.sanity.ipv4.sync.test_put import *
from ..api_ip.tests.unit.ipv4.async.test_delete import *
from ..api_ip.tests.unit.ipv4.async.test_post import *
from ..api_ip.tests.unit.ipv4.async.test_put import *
from ..api_ip.v4.tests.sanity.ipv4.sync.test_delete import *
from ..api_ip.v4.tests.sanity.ipv4.sync.test_get import *
from ..api_ip.v4.tests.sanity.ipv4.sync.test_post import *
from ..api_ip.v4.tests.sanity.ipv4.sync.test_put import *


# Tests for IPV6
from ..api_ip.tests.sanity.ipv6.sync.test_delete import *
from ..api_ip.tests.sanity.ipv6.sync.test_get import *
from ..api_ip.tests.sanity.ipv6.sync.test_post import *
from ..api_ip.tests.sanity.ipv6.sync.test_put import *
from ..api_ip.tests.unit.ipv6.async.test_delete import *
from ..api_ip.tests.unit.ipv6.async.test_post import *
from ..api_ip.v4.tests.sanity.ipv6.sync.test_delete import *
from ..api_ip.v4.tests.sanity.ipv6.sync.test_get import *
from ..api_ip.v4.tests.sanity.ipv6.sync.test_post import *
from ..api_ip.v4.tests.sanity.ipv6.sync.test_put import *


# Tests for Environment
from ..api_environment.tests.sanity.test_cidr_delete import *
from ..api_environment.tests.sanity.test_cidr_get import *
from ..api_environment.tests.sanity.test_cidr_post import *
from ..api_environment.tests.sanity.test_cidr_put import *
from ..api_environment.tests.sanity.test_environment_delete import *
from ..api_environment.tests.sanity.test_environment_get import *
from ..api_environment.tests.sanity.test_environment_post import *
from ..api_environment.tests.sanity.test_environment_put import *
from ..api_environment.tests.test_acl_flows import *


# Tests for Environment VIP
from ..api_environment_vip.tests.sanity.test_environment_vip_delete import *
from ..api_environment_vip.tests.sanity.test_environment_vip_get import *
from ..api_environment_vip.tests.sanity.test_environment_vip_post import *
from ..api_environment_vip.tests.sanity.test_environment_vip_put import *


# Tests for Plugins
from ..plugins.SDN.ODL.tests.test_acl_flow_builder import *
from ..plugins.SDN.ODL.tests.test_cookie_handler import *
from ..plugins.SDN.ODL.tests.test_generic_odl_plugin import *
from ..plugins.SDN.ODL.tests.test_odl_acl import *
from ..plugins.SDN.ODL.tests.test_odl_authentication import *
from ..plugins.SDN.ODL.tests.test_send_flows_with_tcp_flags import *
from ..plugins.SDN.ODL.tests.test_tcp_control_bits import *


# Tests for Network v4
from ..api_network.tests.test_create_network import *
from ..api_network.tests.test_facade import *
from ..api_network.tests.v3.unit.networkipv4.async.test_delete import *
from ..api_network.tests.v3.unit.networkipv4.async.test_post import *
from ..api_network.tests.v3.unit.networkipv4.async.test_put import *
from ..api_network.tests.v3.sanity.allocate.test_network_v4 import *
from ..api_network.tests.v3.sanity.networkipv4.sync.test_delete import *
from ..api_network.tests.v3.sanity.networkipv4.sync.test_get import *
from ..api_network.tests.v3.sanity.networkipv4.sync.test_post import *
from ..api_network.tests.v3.sanity.networkipv4.sync.test_put import *


# Tests for Network v6
from ..api_network.tests.v3.unit.networkipv6.async.test_delete import *
from ..api_network.tests.v3.unit.networkipv6.async.test_post import *
from ..api_network.tests.v3.unit.networkipv6.async.test_put import *
from ..api_network.tests.v3.sanity.allocate.test_network_v4 import *
from ..api_network.tests.v3.sanity.networkipv6.sync.test_delete import *
from ..api_network.tests.v3.sanity.networkipv6.sync.test_get import *
from ..api_network.tests.v3.sanity.networkipv6.sync.test_post import *
from ..api_network.tests.v3.sanity.networkipv6.sync.test_put import *


# Tests for ASN
from ..api_asn.v4.tests.sanity.sync.test_as_delete import *
from ..api_asn.v4.tests.sanity.sync.test_as_get import *
from ..api_asn.v4.tests.sanity.sync.test_as_post import *
from ..api_asn.v4.tests.sanity.sync.test_as_put import *


# Tests for Interface
from ..api_interface.tests.sanity.interface.test_interface_delete import *
from ..api_interface.tests.sanity.interface.test_interface_get import *
from ..api_interface.tests.sanity.interface.test_interface_post import *
from ..api_interface.tests.sanity.interface.teste_interface_put import *
from ..api_interface.tests.sanity.interface_environments.teste_delete import *
from ..api_interface.tests.sanity.interface_environments.teste_post import *


# Tests for List Configuration BGP
from ..api_list_config_bgp.v4.tests.sanity.sync.test_delete import *
from ..api_list_config_bgp.v4.tests.sanity.sync.test_get import *
from ..api_list_config_bgp.v4.tests.sanity.sync.test_post import *
from ..api_list_config_bgp.v4.tests.sanity.sync.test_put import *


# Tests for Rack
from ..api_rack.tests.datacenter.test_datacenter import *
from ..api_rack.tests.fabric.test_fabric import *
from ..api_rack.tests.rack.test_rack import *


# Tests for Pool
from ..api_pools.tests.functional.v1.test_facade import *
from ..api_pools.tests.functional.v1.test_save_pool import *
from ..api_pools.tests.sanity.test_pool_deploy_mock_delete import *
from ..api_pools.tests.sanity.test_pool_deploy_mock_post import *
from ..api_pools.tests.sanity.test_pool_deploy_mock_put import *
from ..api_pools.tests.sanity.test_pool_get import *
from ..api_pools.tests.sanity.test_pool_get_deploy_mock import *
from ..api_pools.tests.sanity.test_pool_post_spec import *
from ..api_pools.tests.sanity.test_pool_put_spec import *
from ..api_pools.tests.unit.test_pool_deploy_mock_plugin import *
from ..api_pools.tests.unit.async.test_delete import *
from ..api_pools.tests.unit.async.test_post import *
from ..api_pools.tests.unit.async.test_put import *


# Tests for VIP Requests
from ..api_vip_request.tests.sanity.sync.test_delete import *
from ..api_vip_request.tests.sanity.sync.test_get import *
from ..api_vip_request.tests.sanity.sync.test_post import *
from ..api_vip_request.tests.sanity.sync.test_put import *
from ..api_vip_request.tests.unit.async.test_delete import *
from ..api_vip_request.tests.unit.async.test_post import *
from ..api_vip_request.tests.unit.async.test_put import *

