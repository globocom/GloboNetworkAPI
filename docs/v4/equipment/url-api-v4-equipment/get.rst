.. _url-api-v4-equipment-get:

GET
###

Obtaining list of Equipments
****************************

It is possible to specify in several ways fields desired to be retrieved in Equipment module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Equipment module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation. Some expandable fields that do not have documentation have its childs described here too because some of these childs are also expandable.):

    * id
    * name
    * maintenance
    * **equipment_type**
    * **model**
        * name
        * **brand**
            * id
            * name
    * **ipsv4**
        * :ref:`ip <url-api-v4-ipv4-get>`
        * :ref:`virtual-interface <url-api-v4-virtual-interface-get>`
    * **ipsv6**
        * :ref:`ip <url-api-v4-ipv6-get>`
        * :ref:`virtual-interface <url-api-v4-virtual-interface-get>`
    * **environments**
        * :ref:`environment <url-api-v4-environment-get>`
        * :ref:`equipment <url-api-v4-equipment-get>`
    * **groups**
    * :ref:`id_as <url-api-v4-as-get>`

Obtaining list of Equipments through some Optional GET Parameters
=================================================================

URL::

    /api/v4/equipment/

Optional GET Parameters::

    rights_write=[string]
    environment=[integer]
    ipv4=[string]
    ipv6=[string]
    is_router=[integer]
    name=[string]

.. TODO ver o que rights_write deve receber

Where:

* **rights_write** must receive 1 if desired to obtain the equipments where at least one group to which the user logged in is related has write access.
* **environment** is some environment identifier.
* **ipv4** and **ipv6** are IP's must receive some valid IP Adresss.
* **is_router** must receive 1 if only router equipments are desired, 0 if only equipments that is not routers are desired.
* **name** is a unique string that only one equipment has.

Example:

With environment and ipv4 GET Parameter::

    /api/v4/equipment/?ipv4=192.168.0.1&environment=5


Obtaining list of Equipments through id's
=========================================

URL::

    /api/v4/equipment/[equipment_ids]/

where **equipment_ids** are the identifiers of Equipments desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/equipment/1/

Many IDs::

    /api/v4/equipment/1;3;8/


Obtaining list of Equipments through extended search
====================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v4/equipment/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v4/equipment/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "maintenance": false,
            "tipo_equipamento": 1
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

Example with fields id, name and maintenance::

    fields=id,name,maintenance


Using **kind** GET parameter
****************************

The Equipment module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*. For example, the field equipment_type for *basic* will contain only the identifier and for *details* will contain also the description.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "equipments": [
            {
                "id": <integer>,
                "name": <string>
            }, ...
        ]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "equipments": [
            {
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
                "ipsv4": [
                    {
                        "ip": {
                            "id": <integer>,
                            "oct4": <integer>,
                            "oct3": <integer>,
                            "oct2": <integer>,
                            "oct1": <integer>,
                            "networkipv4": {
                                "id": <integer>,
                                "oct1": <integer>,
                                "oct2": <integer>,
                                "oct3": <integer>,
                                "oct4": <integer>,
                                "prefix": <integer>,
                                "networkv4": <string>,
                                "mask_oct1": <integer>,
                                "mask_oct2": <integer>,
                                "mask_oct3": <integer>,
                                "mask_oct4": <integer>,
                                "mask_formated": <string>,
                                "broadcast": <string>,
                                "vlan": {
                                    "id": <integer>,
                                    "name": <string>,
                                    "num_vlan": <integer>,
                                    "environment": <integer>,
                                    "description": <string>,
                                    "acl_file_name": <string>,
                                    "acl_valida": <boolean>,
                                    "acl_file_name_v6": <string>,
                                    "acl_valida_v6": <boolean>,
                                    "active": <boolean>,
                                    "vrf": <string>,
                                    "acl_draft": <string>,
                                    "acl_draft_v6": <string>
                                },
                                "network_type": {
                                    "id": <integer>,
                                    "tipo_rede": <string>
                                },
                                "environmentvip": {
                                    "id": <integer>,
                                    "finalidade_txt": <string>,
                                    "cliente_txt": <string>,
                                    "ambiente_p44_txt": <string>,
                                    "description": <string>
                                },
                                "active": <boolean>,
                                "dhcprelay": [
                                    {
                                        "id": <integer>,
                                        "ipv4": <integer>,
                                        "networkipv4": <integer>
                                    }, ...
                                ],
                                "cluster_unit": <string>
                            },
                            "description": <string>
                        },
                        "virtual_interface": {
                            "id": <integer>,
                            "name": <string>,
                            "vrf": {
                                "id": <integer>,
                                "internal_name": <string>,
                                "vrf": <string>
                            }
                        }
                    }, ...
                ],
                "ipsv6": [
                    {
                        "ip": {
                            "id": 1,
                            "block1": <string>,
                            "block2": <string>,
                            "block3": <string>,
                            "block4": <string>,
                            "block5": <string>,
                            "block6": <string>,
                            "block7": <string>,
                            "block8": <string>,
                            "networkipv6": {
                                "id": <integer>,
                                "block1": <string>,
                                "block2": <string>,
                                "block3": <string>,
                                "block4": <string>,
                                "block5": <string>,
                                "block6": <string>,
                                "block7": <string>,
                                "block8": <string>,
                                "prefix": <integer>,
                                "networkv6": <string>,
                                "mask1": <string>,
                                "mask2": <string>,
                                "mask3": <string>,
                                "mask4": <string>,
                                "mask5": <string>,
                                "mask6": <string>,
                                "mask7": <string>,
                                "mask8": <string>,
                                "mask_formated": <string>,
                                "vlan": {
                                    "id": <integer>,
                                    "name": <string>,
                                    "num_vlan": <integer>,
                                    "environment": <integer>,
                                    "description": <string>,
                                    "acl_file_name": <string>,
                                    "acl_valida": <boolean>,
                                    "acl_file_name_v6": <string>,
                                    "acl_valida_v6": <boolean>,
                                    "active": <boolean>,
                                    "vrf": <integer>,
                                    "acl_draft": <string>,
                                    "acl_draft_v6": <string>
                                },
                                "network_type": {
                                    "id": <integer>,
                                    "tipo_rede": <string>
                                },
                                "environmentvip": {
                                    "id": <integer>,
                                    "finalidade_txt": <string>,
                                    "cliente_txt": <string>,
                                    "ambiente_p44_txt": <string>,
                                    "description": <string>
                                },
                                "active": <boolean>,
                                "dhcprelay": [
                                    {
                                        "id": <integer>,
                                        "ipv6": <integer>,
                                        "networkipv6": <integer>
                                    }, ...
                                ],
                                "cluster_unit": <string>
                            },
                            "description": <string>
                        },
                        "virtual_interface": {
                            "id": <integer>,
                            "name": <string>,
                            "vrf": {
                                "id": <integer>,
                                "internal_name": <string>,
                                "vrf": <string>
                            }
                        }
                    }, ...
                ],
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
                            "father_environment": <recurrence-to:environment>,
                            "sdn_controllers": null
                        }
                    }, ...
                ],
                "groups": [
                    {
                        "id": <integer>,
                        "name": <string>
                    }, ...
                ],
                "id_as": {
                    "id": <integer>,
                    "name": <string>,
                    "description": <string>
                }
            }, ...
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
        "equipments": [
            {
                "id": <integer>,
                "name": <string>,
                "maintenance": <boolean>,
                "equipment_type": <integer>,
                "model": <integer>
            }, ...
        ]
    }
