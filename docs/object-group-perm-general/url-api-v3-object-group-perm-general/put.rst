PUT
###

.. _url-api-v3-object-group-perm-general-put-update-list-object-group-perm-general:

Updating list of General Object Group Permissions objects
*********************************************************

URL::

    /api/v3/object-group-perm-general/

Request body:

.. code-block:: json

    {
        "ogpgs": [{
            "user_group": <integer>,
            "object_type": <integer>,
            "read": <boolean>,
            "write": <boolean>,
            "change_config": <boolean>,
            "delete": <boolean>
        },..]
    }

Request Example:

.. code-block:: json

    {
        "ogpgs": [{
            "user_group": 5,
            "object_type": 3
            "read": true,
            "write": false,
            "change_config": false,
            "delete": false
        }]
    }

Through General Object Group Permissions PUT route you can change permissions assigned for a class of objects to some user group. Remember that general permissions do not prevail over individual if it exists. Only **id** is required:

* **id** - Its the identifier fo the general permission.
* **read** - Tell if the users of group identified by **user_group** will have read rights about objects of type identified by **object_type**.
* **write** - Tell if the users of group identified by **user_group** will have write rights about objects of type identified by **object_type**.
* **change_config** - Tell if the users of group identified by **user_group** will have change config rights about objects of type identified by **object_type**.
* **delete** - Tell if the users of group identified by **user_group** will have delete rights about objects of type identified by **object_type**.

At the end of PUT request, it will be returned the identifiers of General Object Group Permissions objects updated.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two General Object Group Permissions objects updated:

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

    /api/v3/object-group-perm-general/

