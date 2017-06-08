POST
####

.. _url-api-v3-networkv6-post-create-list-networkv6:

Creating list of IPv6 objects
*****************************

URL::

    /api/v3/networkv6/

Request body:

.. code-block:: json

    {
        "networks": [{
            "block1": <string>,
            "block2": <string>,
            "block3": <string>,
            "block4": <string>,
            "block5": <string>,
            "block6": <string>,
            "block7": <string>,
            "block8": <string>,
            "prefix": <integer>,
            "mask1": <string>,
            "mask2": <string>,
            "mask3": <string>,
            "mask4": <string>,
            "mask5": <string>,
            "mask6": <string>,
            "mask7": <string>,
            "mask8": <string>,
            "vlan": <integer>,
            "network_type": <integer>,
            "environmentvip": <integer>,
            "cluster_unit": <string>,
        },..]
    }

Request Example with only required fields:

.. code-block:: json

    {
        "networks": [{
            "vlan": 10
        }]
    }

Request Example with some more fields:

.. code-block:: json

    {
        "networks": [{
            "block1": "fdbe",
            "block2": "bebe",
            "block3": "bebe",
            "block4": "bebe",
            "block5": "0000",
            "block6": "0000",
            "block7": "0000",
            "block8": "0000",
            "prefix": 64,
            "network_type": 5,
            "environmentvip": 5,
            "vlan": 5
        }]
    }

Through Network IPv6 POST route you can create one or more Network IPv6 objects. Only "vlan" field are required. You can specify other fields such as:

* **block1**, **block2**, **block3**, **block4**, **block5**, **block6**, **block7**, **block8** - Are the octets of Network IPv6. Given an Vlan, API can provide automatically a Network IPv6 range to you, but it's possible to assign a Network IPv6 range respecting limits defined in Vlan. If you specify some octet, you need to specify all the others.
* **mask1**, **mask2**, **mask3**, **mask4**, **mask5**, **mask6**, **mask7**, **mask8** and **prefix** - If you specify octets of Network IPv6, it' mandatory to specify the mask by octets or by prefix.
* **network_type** - Says if it's a valid/invalid network of Vip Requests, Equipments or NAT.
* **environmentvip** - Use it to associate a new Network IPv6 to an existent Environment Vip

At the end of POST request, it will be returned the identifiers of new Network IPv6 objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two Network IPv6 objects created:

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

    /api/v3/networkv6/

