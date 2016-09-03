GET
###

Obtaining list of pools with member states updated
**************************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/member/status/

where **pool_ids** are the identifiers of each pool desired to be obtained. To obtain more than one pool, semicolons between the identifiers should be used.

GET Param::

    checkstatus=[0|1]

To obtain member states **updated**, checkstatus should be assigned to 1. If it is assigned to 0, server pools will be retrieved but the real status of the equipments will not be checked in the equipment.

Response body:

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

Pool Member
===========

* **member_status** in "server_pool_members must receive a value ranging from 0 to 7. These value will be converted into binary format. On PUT, first bit will be ignored because in the equipment it's read-only
* **member_status** format: X X X where **X** is 0 or 1.
    * First bit:
        * User up - 1
        * User down - 0
    * Second bit:
        * Enable member - 1
        * Disable member - 0
    * Third bit (**read-only**):
        * Healthcheck status is up - 1
        * Healthcheck status is down - 0

