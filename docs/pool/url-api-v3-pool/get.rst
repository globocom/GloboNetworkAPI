GET
###

Obtaining server pools through id's
***********************************

URL::

    /api/v3/pool/<pool_ids>/

where **pool_ids** are the identifiers of each pool desired to be obtained. To obtain more than one pool, semicolons between the identifiers should be used.

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
        },..]
    }


Obtaining server pools through extended search
**********************************************

URL::

    /api/v3/pool/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/pool/?search=[dict encoded]

Request body:

.. code-block:: json

    {
        'extends_search': [{
            'environment': <environment_id>
        }],
        'start_record': <integer>,
        'custom_search': '<string>',
        'end_record': <integer>,
        'asorting_cols': [<string>,..],
        'searchable_columns': [<string>,..]
    }

Request body example:

.. code-block:: json

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

Response body:

.. code-block:: json

    {
        "total" [integer],
        "server_pools": [...]
    }