PATCH
#####

.. _url-api-v3-vlan-patch-partially-update-list-vlans:

Partially updating list of Vlans in database
********************************************

URL::

    /api/v3/vlan/

Request body:

.. code-block:: json

    {
        "vlans": [{
            "id": [integer],
            "active": [boolean]
        },..]
    }

Request Example:

.. code-block:: json

    {
        "vlans": [{
            "id": 1,
            "active": false
        }]
    }

In Vlan PATCH request, you only need to specify the fields you want to change. For now, only **active** field can be changed.

* **active** - If not specified, Vlan will be the same as before. If specified, it will be updated with the new value.
