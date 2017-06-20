PUT
###

.. _url-api-v3-ipv4-put-update-list-ipv4s:

Updating list of IPv4 objects in database
*****************************************

URL::

    /api/v3/ipv4/[ipv4_ids]/

where **ipv4_ids** are the identifiers of IPv4 objects. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/ipv4/1/

Many IDs::

    /api/v3/ipv4/1;3;8/

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

In IPv4 PUT request, you can only change description and associations with equipments.

* **id** - Identifier of IPv4 that will be changed. It's mandatory.
* **description** - Description of new IPv4.
* **equipments** - You can create new associations with equipments when updating IPv4. Old associations will be deleted even you don't specify new associations to other equipments.

URL Example::

    /api/v3/ipv4/1/

