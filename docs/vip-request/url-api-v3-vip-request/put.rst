PUT
###

Updating list of vip request in database
****************************************

URL::

/api/v3/vip-request/[vip_request_ids]/

where **vip_request_ids** is the identifier of vip request. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

/api/v3/vip-request/1/

Many IDs::

/api/v3/vip-request/1;3;8/

Request body:

.. code-block:: json

    {
        "vips": [{
            "business": [string],
            "created": [boolean],
            "environmentvip": [environmentvip_id],
            "id": [vip_id],
            "ipv4": [ipv4_id],
            "ipv6": [ipv6_id],
            "name": [string],
            "options": {
                "cache_group": [optionvip_id],
                "persistence": [optionvip_id],
                "timeout": [optionvip_id],
                "traffic_return": [optionvip_id]
            },
            "ports": [{
                "id": [vip_port_id],
                "options": {
                    "l4_protocol": [optionvip_id],
                    "l7_protocol": [optionvip_id]
                },
                "pools": [{
                        "l7_rule": [optionvip_id],
                        "l7_value": [string],
                        "order": [interger],
                        "server_pool": [server_pool_id]
                    },..],
                "port": [integer]
                },..],
            "service": [string]
        },..]
    }

* "environmentvip" attribute is an integer that identifies the environment vip that is desired to associate to the existent vip request.
* "options" are the configured options vip that is desired to associate to the existent vip request.
    * cache-group, persistence, timeout and traffic_return are some values present in the database. These values are configured to a set of restricted values.
* "ports" are the configured ports that is desired to asssociate to the existent vip request.
    * l4_protocol and l7_protocol in options and l7_rule in pools work as well as the values present in "options" discussed above.
    * "server_pool" is the identifier of the server-pool port associated to the existent vip request.

URL Examples::

/api/v3/vip-request/1/