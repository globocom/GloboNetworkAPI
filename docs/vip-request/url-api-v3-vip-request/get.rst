GET
###

Obtaining list of vip request through ids:
******************************************

URL::

    /api/v3/vip-request/[vip_request_ids]/

where **vip_request_ids** is the identifier of vip request. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/1/

Many IDs::

    /api/v3/vip-request/1;3;8/

Obtaining list of vip request through extended search
*****************************************************

Extended search permits a search with multiple options, according with user desires. In the following example, the attribute **extended-search** receives an array with two dicts where the expected result is a list of vip requests where the ipv4 "192.168.x.x" are created or the ipv4 "x.168.17.x" are not created in the associated server pools. Remember that an OR operation is made to each element in an array and an AND operation is made to each element in an dict. An array can be a value associated to some key into a dict as well as a dict can be an element of an array.

URL::

    /api/v3/vip-request/

GET Parameter::

    search=[dict encoded]

Example::

    /api/v3/vip-request/?search=[dict encoded]

.. code-block:: json

    {
        "extends_search": [{
            "ipv4__oct1": "192",
            "ipv4__oct2": "168",
            "created": true
            },
        {
            "ipv4__oct2": "168",
            "ipv4__oct3": "17",
            "created": false
        }],
        "start_record": 0,
        "custom_search": "",
        "end_record": 25,
        "asorting_cols": [],
        "searchable_columns": []
    }

URL encoded::

    /api/v3/vip-request/?search=%7B%22extends_search%22%3A%2F%2F%5B%7B%22ipv4__oct1%22%22192%22%2C%22ipv4__oct2%22%3A%22168%22%2C%22created%22%3Atrue%7D%2C%7B%22ipv4__oct2%22%3A%22168%22%2C%22ipv4__oct3%22%3A%2217%22%2C%22created%22%3Afalse%7D%5D%2C%22start_record%22%3A0%2C%22custom_search%22%3A%22%22%2C%22end_record%22%3A25%2C%22asorting_cols%22%3A%5B%5D%2C%22searchable_columns%22%3A%5B%5D%7D%7D

Response body:
**************

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
                        "order": [integer],
                        "server_pool": [server_pool_id]
                    },...],
                "port": [integer]
                },...],
            "service": [string]
        },...]
    }

* "environmentvip" attribute is an integer that identifies the environment vip associated to the retrieved vip request.
* "options" are the configured options vip associated to the retrieved vip request.
    * cache-group, persistence, timeout and traffic_return are some values present in the database. These values are configured to a set of restricted values.
* "ports" are the configured ports associated to the retrieved vip request.
    * l4_protocol and l7_protocol in options and l7_rule in pools work as well as the values present in "options" discussed above.
    * "server_pool" is the identifier of the server-pool port associated to the retrieved vip request.

List of vips request when "search" is used, returns "total" property :

.. code-block:: json

    {
        "total": [integer],
        "vips": [...]
    }
