POST
####

.. _url-api-v3-ipv4-post-create-list-ipv4:

Creating list of IPv4 objects
*****************************

URL::

    /api/v3/ipv4/

Request body:

.. code-block:: json

    {
        "ips": [{
            "oct1": <integer>,
            "oct2": <integer>,
            "oct3": <integer>,
            "oct4": <integer>,
            "networkipv4": <integer>,
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
            "networkipv4": 10
        }]
    }

Request Example with some more fields:

.. code-block:: json

    {
        "ips": [{
            "oct1": 10,
            "oct2": 10,
            "oct3": 0,
            "oct4": 20,
            "networkipv4": 2,
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

Through IPv4 POST route you can create one or more IPv4 objects. Only "networkipv4" field are required. You can specify other fields such as:

* **oct1**, **oct2**, **oct3**, **oct4** - Are the octets of IPv4. Given a network, API can provide to you an IPv4 Address automatically, but you can assign a IPv4 Address in a manually way. If you specify some octet, you need to specify all the others.
* **description** - Description of new IPv4.
* **networkipv4** - This parameter is mandatory. It is the network to which new IP address will belong.
* **equipments** - You can associate new IP address to one or more equipments.

At the end of POST request, it will be returned the identifiers of new IPv4 objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two IPv4 objects created:

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

    /api/v3/ipv4/

