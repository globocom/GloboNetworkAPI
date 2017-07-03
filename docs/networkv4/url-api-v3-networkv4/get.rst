.. _url-api-v3-networkv4-get:

GET
###

Obtaining list of Network IPv4 objects
**************************************

It is possible to specify in several ways fields desired to be retrieved in Network IPv4 module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Network IPv4 module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * id
    * oct1
    * oct2
    * oct3
    * oct4
    * prefix
    * networkv4
    * mask_oct1
    * mask_oct2
    * mask_oct3
    * mask_oct4
    * mask_formated
    * broadcast
    * :ref:`vlan <url-api-v3-vlan-get>`
    * **network_type**
    * :ref:`environmentvip <url-api-v3-environment-vip-get>`
    * active
    * dhcprelay
    * cluster_unit


Obtaining list of Network IPv4 objects through id's
===================================================

URL::

    /api/v3/networkv4/[networkv4_ids]/

where **networkv4_ids** are the identifiers of Network IPv4 objects desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/networkv4/1/

Many IDs::

    /api/v3/networkv4/1;3;8/


Obtaining list of Network IPv4 objects through extended search
==============================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/networkv4/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/networkv4/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [
            {
                "oct1": 10,
            },
            {
                "oct1": 172,
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

Example with fields id, networkv4 and mask_formated::

    fields=id,networkv4,mask_formated


Using **kind** GET parameter
****************************

The Network IPv4 module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "networks": [
            {
                "id": <integer>,
                "networkv4": <string>,
                "mask_formated": <string>,
                "broadcast": <string>,
                "vlan": {
                    "id": <integer>,
                    "name": <string>,
                    "num_vlan": <integer>
                },
                "network_type": <integer>,
                "environmentvip": <integer>
            }
        ]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "networks": [
            {
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
                    <string>, ...
                ],
                "cluster_unit": <string>
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
        "networks": [
            {
                "id": <integer>,
                "oct1": <integer>,
                "oct2": <integer,
                "oct3": <integer>,
                "oct4": <integer>,
                "prefix": <integer>,
                "mask_oct1": <integer>,
                "mask_oct2": <integer>,
                "mask_oct3": <integer>,
                "mask_oct4": <integer>,
                "broadcast": <string>,
                "vlan": <integer>,
                "network_type": <integer>,
                "environmentvip": <integer>,
                "active": <boolean>,
                "cluster_unit": <string>
            }
        ]
    }

