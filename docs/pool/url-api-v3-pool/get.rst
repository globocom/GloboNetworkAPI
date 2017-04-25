.. _url-api-v3-pool-get:

GET
###

Obtaining list of Server Pool
*****************************

It is possible to specify in several ways fields desired to be retrieved in Server Pool module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Server Pool module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation. Some expandable fields that do not have documentation have its childs described here too because some of these childs are also expandable.):

    * id
    * identifier
    * default_port
    * :ref:`environment <url-api-v3-environment-get>`
    * **servicedownaction**
    * lb_method
    * **healthcheck**
    * default_limit
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
    * pool_created
    * :ref:`vips <url-api-v3-vip-request-get>`
    * dscp
    * :ref:`groups_permissions <url-api-v3-object-group-perm-get>`


Obtaining list of Server Pools through id's
===========================================

URL::

    /api/v3/pool/<pool_ids>/

where **pool_ids** are the identifiers of each pool desired to be obtained. To obtain more than one pool, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/pool/1/

Many IDs::

    /api/v3/pool/1;3;8/


Obtaining list of Server Pools through extended search
======================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/pool/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/pool/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "environment": 1
        }],
        "start_record": 0,
        "custom_search": "",
        "end_record": 25,
        "asorting_cols": [],
        "searchable_columns": []
    }

* When **search** is used, "total" property is also retrieved.


Using **fields** GET parameter
******************************

Through **fields**, you can specify desired fields.

Example with field id::

    fields=id

Example with fields id, identifier and pool_created::

    fields=id,identifier,pool_created


Using **kind** GET parameter
****************************

The Server Pool module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "server_pools": [{
            "id": <integer>,
            "identifier": <string>,
            "pool_created": <boolean>
        },...]
    }


Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "server_pools": [{
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
            }],
            "pool_created": <boolean>
        }]
    }


Using **fields** and **kind** together
**************************************

If **fields** is being used together **kind**, only the required fields will be retrieved instead of default.

Example with details kind and id field::

    kind=details&fields=id


Default behavior without **kind** and **fields**
************************************************

If neither **kind** nor **fields** are used in request, the response body will look like this::

    {
        "server_pools": [{
            "id": <server_pool_id>,
            "identifier": <string>,
            "default_port": <integer>,
            environmentvip": <environment_id>,
            "servicedownaction": {
                "id": <optionvip_id>,
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
                "id": <server_pool_member_id>,
                "identifier": <string>,
                "ipv6": {
                    "ip_formated": <ipv6_formated>,
                    "id": <ipv6_id>
                },
                "ip": {
                    "ip_formated": <ipv4_formated>,
                    "id": <ipv4_id>
                },
                "priority": <integer>,
                "equipment": {
                    "id": <integer>,
                    "name": <string>
                },
                "weight": <integer>,
                "limit": <integer>,
                "port_real": <integer>,
                "last_status_update_formated": <string>,
                "member_status": <integer>
            },...],
            "pool_created": <boolean>
        },...]
    }

