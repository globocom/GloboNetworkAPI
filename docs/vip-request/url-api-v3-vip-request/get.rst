GET
###

Return list of vip request by ids:
***************************

URL::

/api/v3/vip-request/[vip_request_ids]/

where ``vip_request_ids`` is the identifier of vip request. It can use multiple id's separated by ``;``.

Example with Parameter IDs:

One ID::

/api/v3/vip-request/1/

Many IDs::

/api/v3/vip-request/1;3;8/

Return list of vip request by dict
**********************************

URL::

/api/v3/vip-request/

GET Parameter

search=[dict encoded]

Example::

/api/v3/vip-request/?search=[dict encoded]

Example with dict

Search server pools where the ipv4 "192.168.x.x" are created or the ipv4 "x.168.17.x" are not created

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

Response body::

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

List of vips request when used "search", return property "total"::

{
    "total": [interger],
    "vips": [..]
}
