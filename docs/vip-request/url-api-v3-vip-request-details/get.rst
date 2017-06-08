GET
###

Obtaining list of vip request
*****************************

Obtaining list of vip request with some more details through id's
=================================================================

URL::

    /api/v3/vip-request/details/[vip_request_ids]/

where **vip_request_ids** are the identifiers of vip requests desired to be retrieved with details. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/details/1/

Many IDs::

    /api/v3/vip-request/details/1;3;8/

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
                "port": (integer),
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
                    "order": (integer|null),
                    "l7_value": (string)
                },...]
            },...],
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
        },...]
    }

* **"environmentvip"** attribute receives a dict with some information about the environment vip associated with the retrieved vip request.
* **"options"** are the configured options vip associated to the retrieved vip request.
    * cache-group, persistence, timeout and traffic_return are some values present in the database. These values are configured to a set of restricted values.
* **"ports"** are the configured ports associated to the retrieved vip request.
    * l4_protocol and l7_protocol in options and l7_rule in pools work as well as the values present in **"options"** discussed above.
    * **"server_pool"** attribute receives a dict with some information about the server pool associated to the retrieved vip request.

Obtaining list of vip request with some more details through extended search
============================================================================

Extended search permits a search with multiple options, according with user desires. The following two examples are shown to demonstrate how easy is to use this resource. In the first example, **extended-search** attribute receives an array with two dicts where the expected result is a list of vip requests where the ipv4 "192.168.x.x" are created or the ipv4 "x.168.17.x" are not created in each associated server pools. Remember that an OR operation is made to each element in an array and an AND operation is made to each element in a dict. An array can be a value associated to some key into a dict as well as a dict can be an element of an array.

In the second example, **extended-search** attribute receives an array with only one dict where the expected result is a list of vip requests where the ipv4 "192.x.x.x" are created on each associated server pools and the name of each virtual lan associated with each ipv4 contains the word "G1". This is one of many possibilities offered by Django QuerySet API.  Due to use of **icontains**, the search of "G1" is not case sensitive.

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/vip-request/details/

GET Param::

    search=[encoded dict]

Example::

    /api/v3/vip-request/details/?search=[encoded dict]

First request body example:

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

Second request body example:

.. code-block:: json

    {
        "extends_search": [{
            "ipv4__vlan__nome__icontains": "G1",
            "ipv4__oct1": "192",
            "created": true
            }
        ],
        "start_record": 0,
        "custom_search": "",
        "end_record": 25,
        "asorting_cols": [],
        "searchable_columns": []
    }

URL encoded for first request body example::

    /api/v3/vip-request/details/?search=%22%7B+++++%22extends_search%22%3A+%5B%7B+++++++++%22ipv4__oct1%22%3A+%22192%22%2C+++++++++%22ipv4__oct2%22%3A+%22168%22%2C+++++++++%22created%22%3A+true+++++++++%7D%2C+++++%7B+++++++++%22ipv4__oct2%22%3A+%22168%22%2C+++++++++%22ipv4__oct3%22%3A+%2217%22%2C+++++++++%22created%22%3A+false+++++%7D%5D%2C+++++%22start_record%22%3A+0%2C+++++%22custom_search%22%3A+%22%22%2C+++++%22end_record%22%3A+25%2C+++++%22asorting_cols%22%3A+%5B%5D%2C+++++%22searchable_columns%22%3A+%5B%5D+%7D%22

URL encoded for second request body example::

    /api/v3/vip-request/details/?search=%7B+++++++++%22extends_search%22%3A+%5B%7B+++++++++++++%22ipv4__vlan__nome__icontains%22%3A+%22TVGLOBO%22+%2C+++++++++++++%22ipv4__oct1%22%3A+%22192%22%2C+++++++++++++%22created%22%3A+true+++++++++++++%7D%2C+++++++++%7B+++++++++++++%22ipv4__vlan_nome__icontains%22%3A+%22G1%22%2C+++++++++++++%22ipv4__oct2%22%3A+%22168%22%2C+++++++++++++%22created%22%3A+false+++++++++%7D%5D%2C+++++++++%22start_record%22%3A+0%2C+++++++++%22custom_search%22%3A+%22%22%2C+++++++++%22end_record%22%3A+25%2C+++++++++%22asorting_cols%22%3A+%5B%5D%2C+++++++++%22searchable_columns%22%3A+%5B%5D+++++%7D

Response body:

.. code-block:: json

    {
        "total": [integer],
        "vips": [..]
    }

* When **"search"** is used, "total" property is also retrieved.
* **"environmentvip"** attribute receives a dict with some information about the environment vip associated with the retrieved vip request.
* **"options"** are the configured options vip associated to the retrieved vip request.
    * cache-group, persistence, timeout and traffic_return are some values present in the database. These values are configured to a set of restricted values.
* **"ports"** are the configured ports associated to the retrieved vip request.
    * l4_protocol and l7_protocol in options and l7_rule in pools work as well as the values present in **"options"** discussed above.
    * **"server_pool"** attribute receives a dict with some information about the server pool associated to the retrieved vip request.
