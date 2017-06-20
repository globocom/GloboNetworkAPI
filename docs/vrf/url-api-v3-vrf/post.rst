POST
####

.. _url-api-v3-vrf-post-create-list-vrf:

Creating list of Vrf objects
****************************

URL::

    /api/v3/vrf/

Request body:

.. code-block:: json

    {
        "vrfs": [{
            "vrf": <string>,
            "internal_name": <string>
        },..]
    }

Request Example:

.. code-block:: json

    {
        "vrfs": [{
            "vrf": "BEVrf",
            "internal_name": "BEVrf"
        }]
    }

Through Vrf POST route you can create one or more Vrf objects. All fields are required:

* **vrf**, **internal_name** - Are the names that represent the Vrf.

At the end of POST request, it will be returned the identifiers of new Vrf objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two Vrf objects created:

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

