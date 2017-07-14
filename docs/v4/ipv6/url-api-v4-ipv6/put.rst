PUT
###

.. _url-api-v3-ipv6-put-update-list-ipv6s:

Updating list of IPv6 objects in database
*****************************************

URL::

    /api/v3/ipv6/[ipv6_ids]/

where **ipv6_ids** are the identifiers of IPv6 objects. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/ipv6/1/

Many IDs::

    /api/v3/ipv6/1;3;8/

Request body:

.. code-block:: json

    {
        "ips": [{
            "id": <integer>,
            "description": <string>,
            "equipments": [
                {
                    "id": <integer>
                },...
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
                    "id": 5
                },
                {
                    "id": 6
                }
            ]
        }]
    }

In IPv6 PUT request, you can only change description and associations with equipments.

* **id** - Identifier of IPv6 that will be changed. It's mandatory.
* **description** - Description of new IPv6.
* **equipments** - You can create new associations with equipments when updating IPv6. Old associations will be deleted even you don't specify new associations to other equipments.

URL Example::

    /api/v3/ipv6/1/

