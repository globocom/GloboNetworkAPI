.. _url-api-v3-environment-get:

GET
###

Obtaining list of Environments
******************************

It is possible to specify in several ways fields desired to be retrieved in Environment module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Environment module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * id
    * name
    * **grupo_l3**
    * **ambiente_logico**
    * **divisao_dc**
    * **filter**
    * acl_path
    * ipv4_template
    * ipv6_template
    * link
    * min_num_vlan_1
    * max_num_vlan_1
    * min_num_vlan_2
    * max_num_vlan_2
    * vrf
    * **default_vrf**
    * :ref:`father_environment <url-api-v3-environment-get>`
    * :ref:`children <url-api-v3-environment-get>`
    * **configs**
    * :ref:`routers <url-api-v3-equipment-get>`
    * :ref:`equipments <url-api-v3-equipment-get>`


Obtaining list of Environments through id's
===========================================

URL::

    /api/v3/environment/[environment_ids]/

where **environment_ids** are the identifiers of Environments desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/environment/1/

Many IDs::

    /api/v3/environment/1;3;8/


Obtaining list of Environments through extended search
======================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/environment/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/environment/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "divisao_dc": 1,
            "ambiente_logico__nome": "AmbLog"
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

Example with fields id, name and grupo_l3::

    fields=id,name,grupo_l3


Using **kind** GET parameter
****************************

The Environment module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "environments": [{
            "id": <integer>,
            "name": <string>
        }]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "environments": [{
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
        "environments": [{
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
            "father_environment": <integer>
        },...]
    }

