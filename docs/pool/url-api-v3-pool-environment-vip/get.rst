GET
###

Obtaining server pools associated to environment vips
*****************************************************

URL::

    /api/v3/pool/environment-vip/<environment_vip_id>/

where **environment_vip_id** is the identifier of the environment vip used as an argument to retrieve associated server pools. Only one **environment_vip_id** can be assigned.

Example::

    /api/v3/pool/1/

Response body:

.. code-block:: json

    {
        "server_pools": [{
            "id": <server_pool_id>,
            "identifier": <string>,
            "default_port": <integer>,
            "environmentvip": <environment_id>,
            "servicedownaction": {
                "id": <optionvip_id>,
                "name": <string>
            },
            "lb_method": <string>,
            "healthcheck": {
                "identifier": <string>,
                "healthcheck_type": <string>,
                "healthcheck_request": <string>,
                "healthcheck_expect": <string>,
                "destination": <string>
            },
            "default_limit": <integer>,
            "server_pool_members": [{
                "id": <server_pool_member_id>,
                "identifier": <string>,
                "ipv6": {
                    "ip_formated": <ipv6_formated>,
                    "id": <ipv6_id>
                },
                "ip": {
                    "ip_formated": <ipv4_formated>,
                    "id": <ipv4_id>
                },
                "priority": <integer>,
                "equipment": {
                    "id": <integer>,
                    "name": <string>
                },
                "weight": <integer>,
                "limit": <integer>,
                "port_real": <integer>,
                "last_status_update_formated": <string>,
                "member_status": <integer>
            }],
            "pool_created": <boolean>
        },..]
    }

Obtaining option vip list by environment id
*******************************************

    Method to return option vip list by environment id
    Param environment_id: environment id
    Return list of option pool
    """