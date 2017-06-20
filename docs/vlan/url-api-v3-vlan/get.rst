.. _url-api-v3-vlan-get:

GET
###

Obtaining list of Vlans
***********************

It is possible to specify in several ways fields desired to be retrieved in Vlan module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Vlan module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * id
    * name
    * num_vlan
    * :ref:`environment <url-api-v3-environment-get>`
    * description
    * acl_file_name
    * acl_valida
    * acl_file_name_v6
    * acl_valida_v6
    * active
    * vrf
    * acl_draft
    * acl_draft_v6
    * :ref:`networks_ipv4 <url-api-v3-networkv4-get>`
    * :ref:`networks_ipv6 <url-api-v3-networkv6-get>`
    * :ref:`vrfs <url-api-v3-vrf-get>`
    * :ref:`groups_permissions <url-api-v3-object-group-perm-get>`


Obtaining list of Vlans through id's
====================================

URL::

    /api/v3/vlan/[vlan_ids]/

where **vlan_ids** are the identifiers of Vlans desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vlan/1/

Many IDs::

    /api/v3/vlan/1;3;8/


Obtaining list of Vlans through extended search
===============================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/vlan/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/vlan/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "num_vlan": 1,
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

Example with fields id, name and num_vlan::

    fields=id,name,num_vlan


Using **kind** GET parameter
****************************

The Vlan module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "vlans": [{
            "id": <integer>,
            "name": <string>,
            "num_vlan": <integer>
        }]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "vlans": [{
            "id": <integer>,
            "name": <string>,
            "num_vlan": <integer>,
            "environment": {
                "id": <integer>,
                "name": <string>,
                "grupo_l3": {
                    "id": <integer>,
                    "name": <string>
                },
                "ambiente_logico": {
                    "id": <integer>,
                    "name": <string>
                },
                "divisao_dc": {
                    "id": <integer>,
                    "name": <string>
                },
                "filter": <integer>,
                "acl_path": <string>,
                "ipv4_template": <string>,
                "ipv6_template": <string>,
                "link": <string>,
                "min_num_vlan_1": <integer>,
                "max_num_vlan_1": <integer>,
                "min_num_vlan_2": <integer>,
                "max_num_vlan_2": <integer>,
                "default_vrf": {
                    "id": <integer>,
                    "internal_name": <string>,
                    "vrf": <string>
                },
                "father_environment": <recurrence-to:environment>
            },
            "description": <string>,
            "acl_file_name": <string>,
            "acl_valida": <boolean>,
            "acl_file_name_v6": <string>,
            "acl_valida_v6": <boolean>,
            "active": <boolean>,
            "vrf": <string>,
            "acl_draft": <string>,
            "acl_draft_v6": <string>
        }]
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
        "vlans": [{
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
        },...]
    }

