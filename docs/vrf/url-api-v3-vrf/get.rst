.. _url-api-v3-vrf-get:

GET
###

Obtaining list of Vrfs
**********************

It is possible to specify in several ways fields desired to be retrieved in Vrf module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Vrf module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * id
    * internal_name
    * vrf

Obtaining list of Vrfs through id's
===================================

URL::

    /api/v3/vrf/[vrf_ids]/

where **vrf_ids** are the identifiers of Vrfs desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vrf/1/

Many IDs::

    /api/v3/vrf/1;3;8/


Obtaining list of Vrfs through extended search
==============================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/vrf/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/vrf/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "vrf__contains": "Default",
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

Example with fields id and internal_name::

    fields=id,internal_name


Using **kind** GET parameter
****************************

The Vrf module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "vrfs": [
            {
                "id": <integer>,
                "internal_name": <string>,
                "vrf": <string>
            },...
        ]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "vrfs": [
            {
                "id": <integer>,
                "internal_name": <string>,
                "vrf": <string>
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
        "vrfs": [
            {
                "id": <integer>,
                "internal_name": <string>,
                "vrf": <string>
            },...
        ]
    }
