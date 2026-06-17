PATCH
#####

.. _url-api-v3-networkv4-patch-partially-update-list-networkv4:

Partially updating list of Networkv4 in database
************************************************

URL::

    /api/v3/networkv4/force/

Request body:

.. code-block:: json

    {
        "networks": [{
            "id": [integer],
            "active": [boolean]
        },..]
    }

Request Example:

.. code-block:: json

    {
        "networks": [{
            "id": 1,
            "active": false
        }]
    }

In Networkv4 PATCH request, you only need to specify the fields you want to change. For now, only **active** field can be changed.

* **active** - If not specified, Networkv4 will be the same as before. If specified, it will be updated with the new value.
