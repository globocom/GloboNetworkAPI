PUT
###

.. _url-api-v4-ipv6-put-update-list-ipv6s:

Updating list of IPv6 objects in database
*****************************************

URL::

    /api/v4/ipv6/[ipv6_ids]/

where **ipv6_ids** are the identifiers of IPv6 objects. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/ipv6/1/

Many IDs::

    /api/v4/ipv6/1;3;8/

Request body:

.. code-block:: json

    {
        "ips": [{
            "id": <integer>,
            "description": <string>,
            "equipments": [
                {
                    "equipment": {
                        "id": <integer>
                    },
                    "virtual_interface": {
                        "id": <integer>
                    }
                }, ...
            ]
        },..]
    }

Request Example:

.. code-block:: json

    {
        "ips": [{
            "id": 1,
            "description": "New description",
            "equipments": [
                {
                    "equipment": {
                        "id": 1
                    },
                    "virtual_interface": {
                        "id": 1
                    }
                },
                {
                    "equipment": {
                        "id": 2
                    }
                }
            ]
        }]
    }

In IPv6 PUT request, you can only change description and associations with equipments.

* **id** - Identifier of IPv6 that will be changed. It's mandatory.
* **description** - Description of new IPv6.
* **equipments** - You can create new associations with equipments and Virtual Interfaces when updating IPv6. Old associations will be deleted even you don't specify new associations to other equipments if all of them not contains a Virtual Interface. If some Virtual Interface appears at least one relationship between IPv6 and Equipment, it can't be deleted and the IPv6 will not be updated.

URL Example::

    /api/v4/ipv6/1/
