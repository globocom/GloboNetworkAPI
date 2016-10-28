GET
###

Obtaining environments associated to environment vip
****************************************************

URL::

    /api/v3/environment/environment-vip/<environment_vip_id>/

where **environment_vip_id** is the identifier of the environment vip used as an argument to retrieve associated environments. Only one **environment_vip_id** can be assigned.

Example::

    /api/v3/environment/environment-vip/1/

Response body:

.. code-block:: json

    {
        "environments": [{
            "id": <integer>,
            "grupo_l3": {
                "id": <integer>,
                "name": <string>
            },
            "ambiente_logico": {
                "id": <integer>,
                "name": <string>
            },
            "divisao_dc": {
                "id": <integer>,
                "name": <string>
            },
            "filter": <integer>,
            "acl_path": <string>,
            "ipv4_template": <string>,
            "ipv6_template": <string>,
            "link": <string>,
            "min_num_vlan_1": <integer>,
            "max_num_vlan_1": <integer>,
            "min_num_vlan_2": <integer>,
            "max_num_vlan_2": <integer>,
            "vrf": <integer>,
            "father_environment": <integer>
        }]
    }


