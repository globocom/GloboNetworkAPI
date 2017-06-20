.. _url-api-v3-equipment-get:

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
    * :ref:`ipv4 <url-api-v3-ipv4-get>`
    * :ref:`ipv6 <url-api-v3-ipv6-get>`
    * **environments**
        * :ref:`environment <url-api-v3-environment-get>`
        * :ref:`equipment <url-api-v3-equipment-get>`
    * **groups**


Obtaining list of Equipments through some Optional GET Parameters
=================================================================

URL::

    /api/v3/equipment/

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

    /api/v3/equipment/?ipv4=192.168.0.1&environment=5


Obtaining list of Equipments through id's
=========================================

URL::

    /api/v3/equipment/[equipment_ids]/

where **equipment_ids** are the identifiers of Equipments desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/equipment/1/

Many IDs::

    /api/v3/equipment/1;3;8/


Obtaining list of Equipments through extended search
====================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/equipment/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/equipment/?search=[encoded dict]

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
        "equipments": [{
            "id": <integer>,
            "name": <string>
        }]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
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
            },
            "ipv4": [{
                "id": <integer>,
                "oct1": <integer>,
                "oct2": <integer>,
                "oct3": <integer>,
                "oct4": <integer>,
                "networkipv4": <integer>,
                "description": <string>
            },...],
            "ipv6": [{
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
            },...],
            "environments": [{
                "is_router": <boolean>,
                "environment": {
                    "id": <integer>,
                    "name": <name>
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
                    "vrf": <string>,
                    "default_vrf": <integer>
                }
            },...],
            "groups": [{
                "id": <integer>,
                "name": <string>
            },...]
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

Response body:

.. code-block:: json

    {
        "equipments": [{
            "id": <integer>,
            "name": <string>,
            "maintenance": <boolean>,
            "equipment_type": <integer>,
            "model": <integer>
        },...]
    }

