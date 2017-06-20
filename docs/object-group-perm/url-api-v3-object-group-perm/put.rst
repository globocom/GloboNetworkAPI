PUT
###

.. _url-api-v3-object-group-perm-put-update-list-object-group-perm:

Updating list of Object Group Permissions objects
*************************************************

URL::

    /api/v3/object-group-perm/

Request body:

.. code-block:: json

    {
        "ogps": [{
            "id": <integer>,
            "read": <boolean>,
            "write": <boolean>,
            "change_config": <boolean>,
            "delete": <boolean>
        },..]
    }

Request Example:

.. code-block:: json

    {
        "ogps": [{
            "id": 5,
            "read": true,
            "write": false,
            "change_config": false,
            "delete": false
        }]
    }

Through Object Group Permissions PUT route you can change permissions assigned for individual objects to some user group. Remember that individual permissions always prevail over general if it exists. Only **id** is required:

* **id** - Its the identifier fo the individual permission.
* **read** - Tell if the users of group identified by **user_group** will have read rights about specific object identified by **object_value** and by its type identified by **object_type**.
* **write** - Tell if the users of group identified by **user_group** will have write rights about specific object identified by **object_value** and by its type identified by **object_type**.
* **change_config** - Tell if the users of group identified by **user_group** will have change config rights about specific object identified by **object_value** and by its type identified by **object_type**.
* **delete** - Tell if the users of group identified by **user_group** will have delete rights about specific object identified by **object_value** and by its type identified by **object_type**.

At the end of PUT request, it will be returned the identifiers of Object Group Permissions objects updated.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two Object Group Permissions objects updated:

.. code-block:: json

    [
        {
            "id": 10
        },
        {
            "id": 11
        }
    ]

URL Example::

    /api/v3/object-group-perm/

