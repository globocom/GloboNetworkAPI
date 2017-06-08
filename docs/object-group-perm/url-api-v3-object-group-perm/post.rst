POST
####

.. _url-api-v3-object-group-perm-post-create-list-object-group-perm:

Creating list of Object Group Permissions objects
*************************************************

URL::

    /api/v3/object-group-perm/

Request body:

.. code-block:: json

    {
        "ogps": [{
            "user_group": <integer>,
            "object_type": <integer>,
            "object_value": <integer>,
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
            "user_group": 5,
            "object_type": 3,
            "object_value": 10,
            "read": true,
            "write": false,
            "change_config": false,
            "delete": false
        }]
    }

Through Object Group Permissions POST route you can assign permissions for individual objects to some user group. Remember that individual permissions always prevail over general if it exists. All fields are required:

* **user_group** -  It receives the identifier of some user group.
* **object_type** - It receives the identifier of some object type.
* **object_value** - It receives the identifier of some object value.
* **read** - Tell if the users of group identified by **user_group** will have read rights about specific object identified by **object_value** and by its type identified by **object_type**.
* **write** - Tell if the users of group identified by **user_group** will have write rights about specific object identified by **object_value** and by its type identified by **object_type**.
* **change_config** - Tell if the users of group identified by **user_group** will have change config rights about specific object identified by **object_value** and by its type identified by **object_type**.
* **delete** - Tell if the users of group identified by **user_group** will have delete rights about specific object identified by **object_value** and by its type identified by **object_type**.

At the end of POST request, it will be returned the identifiers of new Object Group Permissions objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two Object Group Permissions objects created:

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

