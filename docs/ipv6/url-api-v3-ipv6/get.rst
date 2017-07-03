.. _url-api-v3-ipv6-get:

GET
###

Obtaining list of IPv6 objects
******************************

It is possible to specify in several ways fields desired to be retrieved in IPv6 module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for IPv6 module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation. Some expandable fields that do not have documentation have its childs described here too because some of these childs are also expandable.):

    * id
    * ip_formated
    * block1
    * block2
    * block3
    * block4
    * block5
    * block6
    * block7
    * block8
    * :ref:`networkipv6 <url-api-v3-networkv6-get>`
    * description
    * :ref:`equipments <url-api-v3-equipment-get>`
    * :ref:`vips <url-api-v3-vip-request-get>`
    * **server_pool_members**
        * id
        * :ref:`server_pool <url-api-v3-pool-get>`
        * identifier
        * :ref:`ip <url-api-v3-ipv4-get>`
        * :ref:`ipv6 <url-api-v3-ipv6-get>`
        * priority
        * weight
        * limit
        * port_real
        * member_status
        * last_status_update
        * last_status_update_formated
        * :ref:`equipments <url-api-v3-equipment-get>`
        * :ref:`equipment <url-api-v3-equipment-get>`

Obtaining list of IPv6 objects through id's
===========================================

URL::

    /api/v3/ipv6/[ipv6_ids]/

where **ipv6_ids** are the identifiers of IPv6 objects desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/ipv6/1/

Many IDs::

    /api/v3/ipv6/1;3;8/


Obtaining list of IPv6 objects through extended search
======================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/ipv6/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/ipv6/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [
            {
                "block1": "fefe",
            },
            {
                "block1": "fdfd",
            }

        ],
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

Example with fields id, ip_formated and networkipv6::

    fields=id,ip_formated,networkipv6


Using **kind** GET parameter
****************************

The IPv6 module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

{
    "ips": [
        {
            "id": <integer>,
            "ip_formated": <string>,
            "networkipv6": {
                "id": <integer>,
                "networkv6": <string>,
                "mask_formated": <string>,
                "broadcast": <string>,
                "vlan": {
                    "id": <integer>,
                    "name": <string>,
                    "num_vlan": <integer>
                },
                "network_type": <integer>,
                "environmentvip": <integer>
            },
            "description": <string>
        }
    ]
}

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "ips": [
            {
                "id": <integer>,
                "ip_formated": <string>,
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
                        <string>,...
                    ],
                    "cluster_unit": <string>
                },
                "description": <string>
            }
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
        "ips":[
            {
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
            }
        ]
    }

