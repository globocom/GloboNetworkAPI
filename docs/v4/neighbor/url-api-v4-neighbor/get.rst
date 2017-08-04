.. _url-api-v4-neighbor-get:

GET
###

Obtaining list of Neighbors
***************************

It is possible to specify in several ways fields desired to be retrieved in Neighbor module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Neighbor module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation. Some expandable fields that do not have documentation have its childs described here too because some of these childs are also expandable.):

    * id
    * remote_as
    * remote_ip
    * password
    * maximum_hops
    * timer_keepalive
    * timer_timeout
    * description
    * soft_reconfiguration
    * community
    * remove_private_as
    * next_hop_self
    * kind
    * created
    * :ref:`virtual-interface <url-api-v4-virtual-interface-get>`    * **model**

Obtaining list of Equipments through extended search
====================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v4/neighbor/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v4/neighbor/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "community": false,
        }],
        "start_record": 0,
        "custom_search": "",
        "end_record": 25,
        "asorting_cols": [],
        "searchable_columns": []
    }

* When **"search"** is used, "total" property is also retrieved.


Using **fields** GET parameter
******************************

Through **fields**, you can specify desired fields.

Example with field id::

    fields=id

Example with fields id, password and community::

    fields=id,password,community


Using **kind** GET parameter
****************************

The Neighbor module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*. For example, the field virtual_interface for *basic* will contain only the identifier and for *details* will contain a bunch of information.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "neighbors": [{
            "id": <integer>,
            "remote_as": <string>,
            "remote_ip": <string>,
            "password": <string>,
            "maximum_hops": <string>,
            "timer_keepalive": <string>,
            "timer_timeout": <string>,
            "description": <string>,
            "soft_reconfiguration": <boolean>,
            "community": <boolean>,
            "remove_private_as": <boolean>,
            "next_hop_self": <boolean>,
            "kind": <string>,
            "created": <boolean>,
            "virtual_interface": {
                "id": <integer>,
                "name": <string>,
                "vrf": <integer>
            }
        }]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "neighbors": [
            {
                "id": <integer>,
                "remote_as": <string>,
                "remote_ip": <string>,
                "password": <string>,
                "maximum_hops": <string>,
                "timer_keepalive": <string>,
                "timer_timeout": <string>,
                "description": <string>,
                "soft_reconfiguration": <boolean>,
                "community": <boolean>,
                "remove_private_as": <boolean>,
                "next_hop_self": <boolean>,
                "kind": <string>,
                "created": <boolean>,
                "virtual_interface": {
                    "id": <integer>,
                    "name": <string>,
                    "vrf": {
                        "id": <integer>,
                        "internal_name": <string>,
                        "vrf": <string>
                    },
                    "ipv4_equipment": [
                        {
                            "ip": {
                                "id": <integer>,
                                "oct4": <integer>,
                                "oct3": <integer>,
                                "oct2": <integer>,
                                "oct1": <integer>,
                                "networkipv4": <integer>,
                                "description": <string>
                            },
                            "equipment": {
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
                                },
                                "environments": [
                                    {
                                        "is_router": <boolean>,
                                        "is_controller": <boolean>,
                                        "environment": {
                                            "id": <integer>,
                                            "name": <string>,
                                            "grupo_l3": <integer>,
                                            "ambiente_logico": <integer>,
                                            "divisao_dc": <integer>,
                                            "filter": <integer>,
                                            "acl_path": <string>,
                                            "ipv4_template": <string>,
                                            "ipv6_template": <string>,
                                            "link": <string>,
                                            "min_num_vlan_1": <integer>,
                                            "max_num_vlan_1": <integer>,
                                            "min_num_vlan_2": <integer>,
                                            "max_num_vlan_2": <integer>,
                                            "default_vrf": <integer>,
                                            "father_environment": <recursion-to:environment>,
                                            "sdn_controlled": <boolean>
                                        }
                                    },...
                                ],
                                "groups": [
                                    {
                                        "id": <integer>,
                                        "name": <string>
                                    },...
                                ],
                                "id_as": {
                                    "id": <integer>,
                                    "name": <string>,
                                    "description": <string>
                                }
                            }
                        },...
                    ],
                    "ipv6_equipment": [
                        {
                            "ip": {
                                "id": <integer>,
                                "block1": <string>,
                                "block2": <string>,
                                "block3": <string>,
                                "block4": <string>,
                                "block5": <string>,
                                "block6": <string>,
                                "block7": <string>,
                                "block8": <string>,
                                "networkipv6": <integer>,
                                "description": <string>
                            },
                            "equipment": {
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
                                },
                                "environments": [
                                    {
                                        "is_router": <boolean>,
                                        "is_controller": <boolean>,
                                        "environment": {
                                            "id": <integer>,
                                            "name": <string>,
                                            "grupo_l3": <integer>,
                                            "ambiente_logico": <integer>,
                                            "divisao_dc": <integer>,
                                            "filter": <integer>,
                                            "acl_path": <string>,
                                            "ipv4_template": <string>,
                                            "ipv6_template": <string>,
                                            "link": <string>,
                                            "min_num_vlan_1": <integer>,
                                            "max_num_vlan_1": <integer>,
                                            "min_num_vlan_2": <integer>,
                                            "max_num_vlan_2": <integer>,
                                            "default_vrf": <integer>,
                                            "father_environment": <recursion-to:environment>,
                                            "sdn_controlled": <boolean>
                                        }
                                    },...
                                ],
                                "groups": [
                                    {
                                        "id": <integer>,
                                        "name": <string>
                                    },...
                                ],
                                "id_as": {
                                    "id": <integer>,
                                    "name": <string>,
                                    "description": <string>
                                }
                            }
                        },...
                    ]
                }
            },...
        ]
    }


Using **fields** and **kind** together
**************************************

If **fields** is being used together **kind**, only the required fields will be retrieved instead of default.

Example with details kind and id field::

    kind=details&fields=id


Default behavior without **kind** and **fields**
************************************************

If neither **kind** nor **fields** are used in request, the response body will look like this:

Response body:

.. code-block:: json

    {
        "neighbors": [{
            "id": 1,
            "remote_as": <string>,
            "remote_ip": <string>,
            "password": <string>,
            "maximum_hops": <string>,
            "timer_keepalive": <string>,
            "timer_timeout": <string>,
            "description": <string>,
            "soft_reconfiguration": <boolean>,
            "community": <boolean>,
            "remove_private_as": <boolean>,
            "next_hop_self": <boolean>,
            "kind": <string>,
            "created": <boolean>,
            "virtual_interface": 1
        },...]
    }
