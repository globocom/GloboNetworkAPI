POST
####

.. _url-api-v3-ipv6-post-create-list-ipv6:

Creating list of IPv6 objects
*****************************

URL::

    /api/v3/ipv6/

Request body:

.. code-block:: json

    {
        "ips": [{
            "block1": <string>,
            "block2": <string>,
            "block3": <string>,
            "block4": <string>,
            "block5": <string>,
            "block6": <string>,
            "block7": <string>,
            "block8": <string>,
            "networkipv6": <integer>,
            "description": <string>,
            "equipments": [
                {
                    "id": <integer>
                },...
            ]
        },..]
    }

Request Example with only required fields:

.. code-block:: json

    {
        "ips": [{
            "networkipv6": 10
        }]
    }

Request Example with some more fields:

.. code-block:: json

    {
        "ips": [{
            "block1": "fdbe",
            "block2": "fdbe",
            "block3": "0000",
            "block4": "0000",
            "block5": "0000",
            "block6": "0000",
            "block7": "0000",
            "block8": "0000",
            "networkipv6": 2,
            "equipments": [
                {
                    "id": 3
                },
                {
                    "id": 4
                }
            ]
        }]
    }

Through IPv6 POST route you can create one or more IPv6 objects. Only "networkipv6" field are required. You can specify other fields such as:

* **block1**, **block2**, **block3**, **block4**, **block5**, **block6**, **block7** and **block8** - Are the octets of IPv6. Given a network, API can provide to you an IPv6 Address automatically, but you can assign a IPv6 Address in a manually way. If you specify some octet, you need to specify all the others.
* **networkipv6** - This parameter is mandatory. It is the network to which new IP address will belong.
* **description** - Description of new IPv6.
* **equipments** - You can associate new IP address to one or more equipments.

At the end of POST request, it will be returned the identifiers of new IPv6 objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two IPv6 objects created:

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

    /api/v3/ipv6/

