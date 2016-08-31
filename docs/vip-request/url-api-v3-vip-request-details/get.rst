GET
###

List of vip request with details by ids::

URL::

    /api/v3/vip-request/details/[vip_request_ids]/

**vip_request_ids** is the identifier of vip request with details. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/details/1/

Many IDs::

    /api/v3/vip-request/details/1;3;8/

Return list of vip request with details by dict

URL::

    /api/v3/vip-request/details/

GET Param::

    search=[dict encoded]

Example::

    /api/v3/vip-request/details/?search=[dict encoded]

Example with dict:

Search server pools where the ipv4 "192.168.x.x" are created or the ipv4 "x.168.17.x" are not created.

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
        },...],
        "start_record": 0,
        "custom_search": "",
        "end_record": 25,
        "asorting_cols": [],
        "searchable_columns": []
    }

URL encoded::

    /api/v3/vip-request/details/?search=%7B%22extends_search%22%3A%2F%2F%5B%7B%22ipv4__oct1%22%22192%22%2C%22ipv4__oct2%22%3A%22168%22%2C%22created%22%3Atrue%7D%2C%7B%22ipv4__oct2%22%3A%22168%22%2C%22ipv4__oct3%22%3A%2217%22%2C%22created%22%3Afalse%7D%5D%2C%22start_record%22%3A0%2C%22custom_search%22%3A%22%22%2C%22end_record%22%3A25%2C%22asorting_cols%22%3A%5B%5D%2C%22searchable_columns%22%3A%5B%5D%7D%7D

Response body:

.. code-block:: json

    {
        "vips": [{
            "id": (vip_id),
            "name": (string),
            "service": (string),
            "business": (string),
            "environmentvip": {
                "id": (environmentvip_id),
                "finalidade_txt": (string),
                "cliente_txt": (string),
                "ambiente_p44_txt": (string),
                "description": (string)
            },
            "ipv4": {
                "id": (ipv4_id)
                "ip_formated": (ipv4_formated),
                "description": (string)
            },
            "ipv6": null,
            "equipments": [{
                "id": (equipment_id),
                "name": (string),
                "equipment_type": (equipment_type_id),
                "model": (model_id),
                "groups": [(group_id),..]
            }],
            "default_names": [(string),..],
            "dscp": (vip_dscp_id),
            "ports": [{
                "id": (vip_port_id),
                "port": (interger),
                "options": {
                    "l4_protocol": {
                        "id": (optionvip_id),
                        "tipo_opcao": (string),
                        "nome_opcao_txt": (string)
                    },
                    "l7_protocol": {
                        "id": (optionvip_id),
                        "tipo_opcao": (string),
                        "nome_opcao_txt": (string)
                    }
                },
                "pools": [{
                    "id": (vip_port_pool_id),
                    "server_pool": {
                        'id': (server_pool_id),
                        ...information from the pool, same as GET Pool*

                    },
                    "l7_rule": {
                        "id": (optionvip_id),
                        "tipo_opcao": (string),
                        "nome_opcao_txt": (string)
                    },
                    "order": (interger|null),
                    "l7_value": (string)
                },..]
            },..],
            "options": {
                "cache_group": {
                    "id": (optionvip_id),
                    "tipo_opcao": (string),
                    "nome_opcao_txt": (string)
                },
                "traffic_return": {
                    "id": (optionvip_id),
                    "tipo_opcao": (string),
                    "nome_opcao_txt": (string)
                },
                "timeout": {
                    "id": (optionvip_id),
                    "tipo_opcao": (string),
                    "nome_opcao_txt": (string)
                },
                "persistence": {
                    "id": (optionvip_id),
                    "tipo_opcao": (string),
                    "nome_opcao_txt": (string)
                }
            },
            "created": (boolean)
        },..]
    }

GET Pool:

List of vip request with details when "search" is used, returns property "total"

.. code-block:: json

    {
        "total": [interger],
        "vips": [..]
    }
