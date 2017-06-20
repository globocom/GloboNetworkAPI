.. _url-api-v3-environment-vip-get:

GET
###

Obtaining list of Environment Vip
*********************************

It is possible to specify in several ways fields desired to be retrieved in Environment Vip module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Environment Vip module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation. Some expandable fields that do not have documentation have its childs described here too because some of these childs are also expandable):

    * id
    * finalidade_txt
    * cliente_txt
    * ambiente_p44_txt
    * description
    * name
    * conf
    * **optionsvip**
        * **option**
        * :ref:`environment_vip <url-api-v3-environment-vip-get>`
    * **environments**
        * :ref:`environment <url-api-v3-environment-get>`
        * :ref:`environment_vip <url-api-v3-environment-vip-get>`


Obtaining list of Environment Vip through id's
==============================================

URL::

    /api/v3/environment-vip/[environment_vip_ids]/

where **environment_vip_ids** are the identifiers of Environments Vip desired to be retrieved. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/environment-vip/1/

Many IDs::

    /api/v3/environment-vip/1;3;8/


Obtaining list of Environment Vip through extended search
=========================================================

More information about Django QuerySet API, please see::

    :ref:`Django QuerySet API reference <https://docs.djangoproject.com/el/1.10/ref/models/querysets/>`_

URL::

    /api/v3/environment-vip/

GET Parameter::

    search=[encoded dict]

Example::

    /api/v3/environment-vip/?search=[encoded dict]

Request body example:

.. code-block:: json

    {
        "extends_search": [{
            "description__icontains": "BE",
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

Example with fields id, name and environments::

    fields=id,name,environments


Using **kind** GET parameter
****************************

The Environment Vip module also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "environments_vip": [{
            "id": <integer>,
            "name": <string>
        },...]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "environments_vip": [{
            "id": <integer>,
            "finalidade_txt": <string>,
            "cliente_txt": <string>,
            "ambiente_p44_txt": <string>,
            "description": <string>,
            "name": <string>,
            "conf": <string>
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
        "environments_vip": [{
            "id": <integer>,
            "finalidade_txt": <string>,
            "cliente_txt": <string>,
            "ambiente_p44_txt": <string>,
            "description": <string>
        },...]
    }

