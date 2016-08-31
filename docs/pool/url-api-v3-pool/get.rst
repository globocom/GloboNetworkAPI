GET
###

Obtaining servel pools through id's
***********************************

URL::

    /api/v3/pool/<pool_ids>/

Example with Parameter IDs:

One ID::

    /api/v3/pool/1/

Many IDs::

    /api/v3/pool/1;3;8/

Response body:

.. code-block:: json

    {
        "server_pools": [{
            "id": <server_pool_id>,
            "identifier": <string>,
            "default_port": <interger>,
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
            "default_limit": <interger>,
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
                "priority": <interger>,
                "equipment": {
                    "id": <interger>,
                    "name": <string>
                },
                "weight": <interger>,
                "limit": <interger>,
                "port_real": <interger>,
                "last_status_update_formated": <string>,
                "member_status": <interger>
            }],
            "pool_created": <boolean>
        },..]
    }


Obtaining server pools through dicts
************************************

URL::

    /api/v3/pool/

GET Params::

    GET['search']

Request body::

.. code-block:: json

    {
        'extends_search': [{
            'environment': <environment_id>
        }],
        'start_record': <interger>,
        'custom_search': '<string>',
        'end_record': <interger>,
        'asorting_cols': [<string>,..],
        'searchable_columns': [<string>,..]
    }
    :return list of server pool with property "total"
    {
        "total": <interger>,
        "server_pools": [..]
    }
    :example
    {
        'extends_search': [{
            'environment': 1
        }],
        'start_record': 0,
        'custom_search': 'pool_123',
        'end_record': 25,
        'asorting_cols': ['identifier'],
        'searchable_columns': [
            'identifier',
            'default_port',
            'pool_created',
            'healthcheck__healthcheck_type'
        ]
    }

