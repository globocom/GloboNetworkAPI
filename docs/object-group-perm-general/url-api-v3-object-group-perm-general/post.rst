POST
####

.. _url-api-v3-object-group-perm-general-post-create-list-object-group-perm-general:

Creating list of General Object Group Permissions objects
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

Through General Object Group Permissions POST route you can assign permissions for a class of objects to some user group. Remember that general permissions do not prevail over individual if it exists. All fields are required:

* **user_group** -  It receives the identifier of some user group.
* **object_type** - It receives the identifier of some object type.
* **read** - Tell if the users of group identified by **user_group** will have read rights about objects of type identified by **object_type**.
* **write** - Tell if the users of group identified by **user_group** will have write rights about objects of type identified by **object_type**.
* **change_config** - Tell if the users of group identified by **user_group** will have change config rights about objects of type identified by **object_type**.
* **delete** - Tell if the users of group identified by **user_group** will have delete rights about objects of type identified by **object_type**.

At the end of POST request, it will be returned the identifiers of new General Object Group Permissions objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two General Object Group Permissions objects created:

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

