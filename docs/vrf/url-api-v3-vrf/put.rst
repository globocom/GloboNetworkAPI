PUT
###

.. _url-api-v3-vrf-put-update-list-vrf:

Updating list of Vrf objects
****************************

URL::

    /api/v3/vrf/

Request body:

.. code-block:: json

    {
        "vrfs": [{
            "id": <integer>,
            "vrf": <string>,
            "internal_name": <string>
        },..]
    }

Request Example:

.. code-block:: json

    {
        "vrfs": [{
            "id": 1,
            "vrf": "BEVrf",
            "internal_name": "BEVrf"
        }]
    }

Through Vrf PUT route you can update one or more Vrf objects. All fields are required:

* **id** - Identifier of Vrf desired to update.
* **vrf**, **internal_name** - Are the names that represent the Vrf.

At the end of PUT request, it will be returned the identifiers of Vrf objects update.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two Vrf objects updated:

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

    /api/v3/vrf/

