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

* **member_status** in "server_pool_members must receive a octal numeric value (0 to 7). This value will be converted into binary format with each bit representing one status. On PUT, most significant bit (2^2) will be ignored because it's read-only in the equipments.
* **member_status** binary format: NNN where **N** is 0 or 1.
    * First bit (2^0):
        * User up - 1 - new connections allowed, check second bit
        * User down - 0 - allow existing connections to time out, but no new connections are allowed, ignore second bit
    * Second bit (2^1):
        * Enabled member - 1 - new connections allowed
        * Disabled member - 0 - member only process persistent and active connections
    * Third bit (**read-only**)(2^2):
        * Healthcheck status is up - 1 - new connections allowed
        * Healthcheck status is down - 0 - no new connections are send in this state

