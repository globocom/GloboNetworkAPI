.. _url-api-v3-vip-request-get:

GET
###

Obtaining list of Vip Request
*****************************

It is possible to specify in several ways fields desired to be retrieved in Vip Request module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Vip Request module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * id
    * name
    * service
    * business
    * :ref:`environmentvip <url-api-v3-environment-vip-get>`
    * :ref:`ipv4 <url-api-v3-ipv4-get>`
    * :ref:`ipv6 <url-api-v3-ipv6-get>`
    * :ref:`equipments <url-api-v3-equipment-get>`
    * default_names
    * dscp
    * ports
    * **options**
    * :ref:`groups_permissions <url-api-v3-object-group-perm-get>`
    * created

Where:

* **"environmentvip"** attribute is an integer that identifies the environment vip associated to the retrieved vip request.
* **"options"** are the configured options vip associated to the retrieved vip request.
    * cache-group, persistence, timeout and traffic_return are some values present in the database. These values are configured to a set of restricted values.
* **"ports"** are the configured ports associated to the retrieved vip request.
    * l4_protocol and l7_protocol in options and l7_rule in pools work as well as the values present in **"options"** discussed above.
    * **"server_pool"** is the identifier of the server-pool port associated to the retrieved vip request.


Obtaining list of Vip Request through id's
==========================================

URL::

    /api/v3/vip-request/[vip_request_ids]/

where **vip_request_ids** are the identifiers of vip requests desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/1/

Many IDs::

    /api/v3/vip-request/1;3;8/


Obtaining list of Vip Request through extended search
=====================================================

Extended search permits a search with multiple options, according with user desires. The following two examples are shown to demonstrate how easy is to use this resource. In the first example, **extended-search** attribute receives an array with two dicts where the expected result is a list of vip requests where the ipv4 "192.168.x.x" are created or the ipv4 "x.168.17.x" are not created in each associated server pools. Remember that an OR operation is made to each element in an array and an AND operation is made to each element in a dict. An array can be a value associated to some key into a dict as well as a dict can be an element of an array.

In the second example, **extended-search** attribute receives an array with only one dict where the expected result is a list of vip requests where the ipv4 "192.x.x.x" are created on each associated server pools and the name of each virtual lan associated with each ipv4 contains the word "G1". This is one of many possibilities offered by Django QuerySet API.  Due to use of **icontains**, the search of "G1" is not case sensitive.

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/vip-request/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/vip-request/?search=[encoded dict]

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

    /api/v3/vip-request/?search=%22%7B+++++%22extends_search%22%3A+%5B%7B+++++++++%22ipv4__oct1%22%3A+%22192%22%2C+++++++++%22ipv4__oct2%22%3A+%22168%22%2C+++++++++%22created%22%3A+true+++++++++%7D%2C+++++%7B+++++++++%22ipv4__oct2%22%3A+%22168%22%2C+++++++++%22ipv4__oct3%22%3A+%2217%22%2C+++++++++%22created%22%3A+false+++++%7D%5D%2C+++++%22start_record%22%3A+0%2C+++++%22custom_search%22%3A+%22%22%2C+++++%22end_record%22%3A+25%2C+++++%22asorting_cols%22%3A+%5B%5D%2C+++++%22searchable_columns%22%3A+%5B%5D+%7D%22

URL encoded for second request body example::

    /api/v3/vip-request/?search=%7B+++++++++%22extends_search%22%3A+%5B%7B+++++++++++++%22ipv4__vlan__nome__icontains%22%3A+%22TVGLOBO%22+%2C+++++++++++++%22ipv4__oct1%22%3A+%22192%22%2C+++++++++++++%22created%22%3A+true+++++++++++++%7D%2C+++++++++%7B+++++++++++++%22ipv4__vlan_nome__icontains%22%3A+%22G1%22%2C+++++++++++++%22ipv4__oct2%22%3A+%22168%22%2C+++++++++++++%22created%22%3A+false+++++++++%7D%5D%2C+++++++++%22start_record%22%3A+0%2C+++++++++%22custom_search%22%3A+%22%22%2C+++++++++%22end_record%22%3A+25%2C+++++++++%22asorting_cols%22%3A+%5B%5D%2C+++++++++%22searchable_columns%22%3A+%5B%5D+++++%7D

* When **"search"** is used, "total" property is also retrieved.


Using **fields** GET parameter
******************************

Through **fields**, you can specify desired fields.

Example with field id::

    fields=id

Example with fields id, name and created::

    fields=id,name,created


Using **kind** GET parameter
****************************

The Vip Request module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*. For example, the field ipv4 for *basic* will contain only the identifier and for *details* will contain name, the ip formated and description.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "vips": [{
            "id": <integer>,
            "name": <string>,
            "ipv4": <integer>,
            "ipv6": <integer>
        }]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "vips": [{
            "id": <integer>,
            "name": <string>,
            "service": <string>,
            "business": <string>,
            "environmentvip": {
                "id": <integer>,
                "finalidade_txt": <string>,
                "cliente_txt": <string>,
                "ambiente_p44_txt": <string>,
                "description": <string>
            },
            "ipv4": {
                "id": <integer>,
                "ip_formated": <string>,
                "description": <string>
            },
            "ipv6": {
                "id": <integer>,
                "ip_formated": <string>,
                "description": <string>
            },
            "equipments": [{
                "id": <integer>,
                "name": <string>,
                "maintenance": <boolean>,
                "equipment_type": {
                    "id": <integer>,
                    "equipment_type": <string>
                },
                "model": {
                    "id": <integer>,
                    "name": <string>
                }
            },...],
            "default_names": [
                <string>,...
            ],
            "dscp": <integer>,
            "ports": [{
                "id": <integer>,
                "port": <integer>,
                "options": {
                    "l4_protocol": {
                        "id": <integer>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    },
                    "l7_protocol": {
                        "id": <integer>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    }
                },
                "pools": [{
                    "id": <integer>,
                    "server_pool": {
                        "id": <integer>,
                        "identifier": <string>,
                        "default_port": <integer>,
                        "environment": {
                            "id": <integer>,
                            "name": <string>
                        },
                        "servicedownaction": {
                            "id": <integer>,
                            "type": <string>,
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
                            "id": <integer>,
							"server_pool": <integer>,
							"identifier": <string>,
							"ip": {
								"id": <integer>,
								"ip_formated": <string>
							},
							"ipv6": {
								"id": <integer>,
								"ip_formated": <string>
							},
							"priority": <integer>,
							"weight": <integer>,
							"limit": <integer>,
							"port_real": <integer>,
							"member_status": <integer>,
							"last_status_update_formated": <string>,
							"equipment": {
								"id": <integer>,
								"name": <string>
							}
                        },...],
                        "pool_created": <boolean>
                    },
                    "l7_rule": {
                        "id": <integer>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    },
                    "l7_value": <integer>,
                    "order": <integer>
                }]
            },...],
            "options": {
                "cache_group": {
                    "id": <integer>,
                    "tipo_opcao": <string>,
                    "nome_opcao_txt": <string>
                },
                "traffic_return": {
                    "id": <integer>,
                    "tipo_opcao": <string>,
                    "nome_opcao_txt": <string>
                },
                "timeout": {
                    "id": <integer>,
                    "tipo_opcao": <string>,
                    "nome_opcao_txt": <string>
                },
                "persistence": {
                    "id": <integer>,
                    "tipo_opcao": <string>,
                    "nome_opcao_txt": <string>
                }
            },
            "groups_permissions": [{
                "group": {
                    "id": <integer>,
                    "name": <string>
                },
                "read": <boolean>,
                "write": <boolean>,
                "change_config": <boolean>,
                "delete": <boolean>
            },...],
            "created": <boolean>
        },...]
    }


Using **fields** and **kind** together
**************************************

If **fields** is being used together **kind**, only the required fields will be retrieved instead of default.

Example with details kind and id field::

    kind=details&fields=id

Default behavior without **kind** and **fields**
************************************************

If neither **kind** nor **fields** are used in request, the response body will look like this:

.. code-block:: json

    {
        "vips": [{
            "id": <integer>,
            "name": <string>,
            "service": <string>,
            "business": <string>,
            "environmentvip": <integer>,
            "ipv4": <integer>,
            "ipv6": <integer>,
            "ports": [{
                "id": <integer>,
                "port": <integer>,
                "options": {
                    "l4_protocol": <integer>,
                    "l7_protocol": <integer>
                },
                "pools": [{
                    "id": integer,
                    "server_pool": <integer>,
                    "l7_rule": <integer>,
                    "l7_value": <integer>,
                    "order": <integer>
                }, ...]
            }, ...],
            "options": {
                "cache_group": <integer>,
                "traffic_return": <integer>,
                "timeout": <integer>,
                "persistence": <integer>
            },
            "created": <boolean>
        },...]
    }

