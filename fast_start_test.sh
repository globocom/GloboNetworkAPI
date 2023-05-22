#!/bin/sh
source venv/bin/activate

pip install --no-cache --upgrade pip
pip install -r requirements_test.txt


echo "exporting NETWORKAPI_DEBUG"
export NETWORKAPI_LOG_QUEUE=0

echo "exporting DJANGO_SETTINGS_MODULE"
export DJANGO_SETTINGS_MODULE='networkapi.settings_ci'

# Updates the SDN controller ip address
export REMOTE_CTRL_IP=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $2}')
echo "Found SDN controller at $REMOTE_CTRL_IP"

echo "Starting tests.."

# echo "=============== Tests for VLAN ================="
# python manage.py test networkapi/api_vlan.tests.sanity.sync.test_vlan_delete.py
# python manage.py test networkapi/api_vlan.tests.sanity.sync.test_vlan_get.py
# python manage.py test networkapi/api_vlan.tests.sanity.sync.test_vlan_post.py
# python manage.py test networkapi/api_vlan.tests.sanity.sync.test_vlan_put.py
# python manage.py test networkapi/api_vlan.tests.unit.async.test_delete.py
# python manage.py test networkapi/api_vlan.tests.unit.async.test_post.py
# python manage.py test networkapi/api_vlan.tests.unit.async.test_put.py

# echo "=============== Tests for IPV4 ================="
# python manage.py test networkapi/api_ip.tests.sanity.ipv4.sync.test_delete.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv4.sync.test_get.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv4.sync.test_post.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv4.sync.test_put.py
# python manage.py test networkapi/api_ip.tests.unit.ipv4.async.test_delete.py
# python manage.py test networkapi/api_ip.tests.unit.ipv4.async.test_post.py
# python manage.py test networkapi/api_ip.tests.unit.ipv4.async.test_put.py
# python manage.py test networkapi/api_ip.v4.tests.sanity.ipv4.sync.test_delete.py
# python manage.py test networkapi/api_ip.v4.tests.sanity.ipv4.sync.test_get.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv4.sync.test_post.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv4.sync.test_put.py

# echo ""
# echo "=============== Tests for IPV6 ================="
# python manage.py test networkapi/api_ip.tests.sanity.ipv6.sync.test_delete.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv6.sync.test_get.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv6.sync.test_post.py
# python manage.py test networkapi/api_ip.tests.sanity.ipv6.sync.test_put.py
# python manage.py test networkapi/api_ip.tests.unit.ipv6.async.test_delete.py
# python manage.py test networkapi/api_ip.tests.unit.ipv6.async.test_post.py
# python manage.py test networkapi/api_ip.tests.unit.ipv6.async.test_put.py
# python manage.py test networkapi/api_ip.v4.tests.sanity.ipv6.sync.test_delete.py
# python manage.py test networkapi/api_ip.v4.tests.sanity.ipv6.sync.test_get.py
# python manage.py test networkapi/api_ip.v4.tests.sanity.ipv6.sync.test_post.py
# python manage.py test networkapi/api_ip.v4.tests.sanity.ipv6.sync.test_put.py

# echo ""
# echo "=============== Tests for Environment ================="
# python manage.py test networkapi/api_environment.tests.sanity.test_cidr_delete.py
# python manage.py test networkapi/api_environment.tests.sanity.test_cidr_get.py
# python manage.py test networkapi/api_environment.tests.sanity.test_cidr_post.py
# python manage.py test networkapi/api_environment.tests.sanity.test_cidr_put.py
# python manage.py test networkapi/api_environment.tests.sanity.test_environment_delete.py
# python manage.py test networkapi/api_environment.tests.sanity.test_environment_get.py
# python manage.py test networkapi/api_environment.tests.sanity.test_environment_post.py
# python manage.py test networkapi/api_environment.tests.sanity.test_environment_put.py
# python manage.py test networkapi/api_environment.tests.test_acl_flows.py

# echo ""
# echo "=============== Tests for Environment VIP ================="
# python manage.py test networkapi/api_environment_vip.tests.sanity.test_environment_vip_delete.py
# python manage.py test networkapi/api_environment_vip.tests.sanity.test_environment_vip_get.py
# python manage.py test networkapi/api_environment_vip.tests.sanity.test_environment_vip_post.py
# python manage.py test networkapi/api_environment_vip.tests.sanity.test_environment_vip_put.py

# echo ""
# echo "=============== Tests for Plugins ================="
# python manage.py test networkapi/plugins.SDN.ODL.tests.test_acl_flow_builder.py
# python manage.py test networkapi/plugins.SDN.ODL.tests.test_cookie_handler.py
# # python manage.py test networkapi/plugins.SDN.ODL.tests.test_generic_odl_plugin.py
# python manage.py test networkapi/plugins.SDN.ODL.tests.test_odl_acl.py
# python manage.py test networkapi/plugins.SDN.ODL.tests.test_odl_authentication.py
# python manage.py test networkapi/plugins.SDN.ODL.tests.test_send_flows_with_tcp_flags.py
# python manage.py test networkapi/plugins.SDN.ODL.tests.test_tcp_control_bits.py

# echo ""
# echo "=============== Tests for Network v4 ================="
# python manage.py test networkapi/api_network.tests.test_create_network.py
# python manage.py test networkapi/api_network.tests.test_facade.py
# python manage.py test networkapi/api_network.tests.v3.unit.networkipv4.async.test_delete.py
# python manage.py test networkapi/api_network.tests.v3.unit.networkipv4.async.test_post.py
# python manage.py test networkapi/api_network.tests.v3.unit.networkipv4.async.test_put.py
# python manage.py test networkapi/api_network.tests.v3.sanity.allocate.test_network_v4.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv4.sync.test_delete.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv4.sync.test_get.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv4.sync.test_post.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv4.sync.test_put.py

# echo ""
# echo "=============== Tests for Network v6 ================="
# python manage.py test networkapi/api_network.tests.v3.unit.networkipv6.async.test_delete.py
# python manage.py test networkapi/api_network.tests.v3.unit.networkipv6.async.test_post.py
# python manage.py test networkapi/api_network.tests.v3.unit.networkipv6.async.test_put.py
# python manage.py test networkapi/api_network.tests.v3.sanity.allocate.test_network_v4.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv6.sync.test_delete.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv6.sync.test_get.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv6.sync.test_post.py
# python manage.py test networkapi/api_network.tests.v3.sanity.networkipv6.sync.test_put.py

# echo ""
# echo "=============== Tests for ASN ================="
# python manage.py test networkapi/api_asn.v4.tests.sanity.sync.test_as_delete.py
# python manage.py test networkapi/api_asn.v4.tests.sanity.sync.test_as_get.py
# python manage.py test networkapi/api_asn.v4.tests.sanity.sync.test_as_post.py
# python manage.py test networkapi/api_asn.v4.tests.sanity.sync.test_as_put.py

# echo ""
# echo "=============== Tests for Interface ================="
# python manage.py test networkapi/api_interface.tests.sanity.interface.test_interface_delete.py
# python manage.py test networkapi/api_interface.tests.sanity.interface.test_interface_get.py
# python manage.py test networkapi/api_interface.tests.sanity.interface.test_interface_post.py
# python manage.py test networkapi/api_interface.tests.sanity.interface.teste_interface_put.py
# python manage.py test networkapi/api_interface.tests.sanity.interface_environments.teste_delete.py
# python manage.py test networkapi/api_interface.tests.sanity.interface_environments.teste_post.py

# echo ""
# echo "=============== Tests for List Configuration BGP ================="
# python manage.py test networkapi/api_list_config_bgp.v4.tests.sanity.sync.test_delete.py
# python manage.py test networkapi/api_list_config_bgp.v4.tests.sanity.sync.test_get.py
# python manage.py test networkapi/api_list_config_bgp.v4.tests.sanity.sync.test_post.py
# python manage.py test networkapi/api_list_config_bgp.v4.tests.sanity.sync.test_put.py

# echo ""
# echo "=============== Tests for Rack ================="
# python manage.py test networkapi/api_rack.tests.datacenter.test_datacenter.py
# python manage.py test networkapi/api_rack.tests.fabric.test_fabric.py
# python manage.py test networkapi/api_rack.tests.rack.test_rack.py

# echo ""
# echo "=============== Tests for Pool ================="
# python manage.py test networkapi/api_pools.tests.functional.v1.test_facade.py
# python manage.py test networkapi/api_pools.tests.functional.v1.test_save_pool.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_deploy_mock_delete.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_deploy_mock_post.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_deploy_mock_put.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_get.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_get_deploy_mock.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_post_spec.py
# python manage.py test networkapi/api_pools.tests.sanity.test_pool_put_spec.py
# python manage.py test networkapi/api_pools.tests.unit.test_pool_deploy_mock_plugin.py
# python manage.py test networkapi/api_pools.tests.unit.async.test_delete.py
# python manage.py test networkapi/api_pools.tests.unit.async.test_post.py
# python manage.py test networkapi/api_pools.tests.unit.async.test_put.py

# echo ""
# echo "=============== Tests for VIP Requests ================="
# python manage.py test networkapi/api_vip_request.tests.sanity.sync.test_delete.py
# python manage.py test networkapi/api_vip_request.tests.sanity.sync.test_get.py
# python manage.py test networkapi/api_vip_request.tests.sanity.sync.test_post.py
# python manage.py test networkapi/api_vip_request.tests.sanity.sync.test_put.py
# python manage.py test networkapi/api_vip_request.tests.unit.async.test_delete.py
# python manage.py test networkapi/api_vip_request.tests.unit.async.test_post.py
# python manage.py test networkapi/api_vip_request.tests.unit.async.test_put.py

# echo ""
echo "=============== Tests for Neighbor ================="
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v4.sanity.sync.test_delete.py
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v4.sanity.sync.test_get.py
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v4.sanity.sync.test_post.py
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v4.sanity.sync.test_put.py
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v6.sanity.sync.test_delete.py
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v6.sanity.sync.test_get.py
python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v6.sanity.sync.test_post.py
# python manage.py test networkapi/api_neighbor.v4.tests.neighbor_v6.sanity.sync.test_put.py