PUT
###

Enabling/Disabling pool member by list of server pool
*****************************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/member/status/

where **pool_ids** are the identifiers of each pool desired to be updated. To update more than one pool, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/pool/deploy/1/member/status/

Many IDs::

    /api/v3/pool/deploy/1;3;8/member/status/

Request body:

.. code-block:: json

    {
        "server_pools": [{
            "id": <server_pool_id>,
            "server_pool_members": [{
                "id": <server_pool_member_id>,
                "member_status": <integer>
            }]
        },...]
    }

More information about the PUT request can be obtained in::

    /api/v3/help/pool_put/

Updating pools by list in equipments
************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/

Request body:

.. code-block:: json

    {
        "server_pools": [{
            "id": <server_pool_id>,
            "identifier": <string>,
            "default_port": <integer>,
            environmentvip": <environment_id>,
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
        },...]
    }

URL Example::

    /api/v3/pool/

More information about the PUT request can be obtained in::

    /api/v3/help/pool_put/

