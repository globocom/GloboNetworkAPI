POST
####

.. _url-api-v3-networkv4-post-create-list-networkv4:

Creating list of IPv4 objects
*****************************

URL::

    /api/v3/networkv4/

Request body:

.. code-block:: json

    {
        "networks": [{
            "oct1": <integer>,
            "oct2": <integer>,
            "oct3": <integer>,
            "oct4": <integer>,
            "prefix": <integer>,
            "mask_oct1": <integer>,
            "mask_oct2": <integer>,
            "mask_oct3": <integer>,
            "mask_oct4": <integer>,
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
            "oct1": 10,
            "oct2": 0,
            "oct3": 0,
            "oct4": 0,
            "prefix": 24,
            "network_type": 5,
            "environmentvip": 5,
            "vlan": 5
        }]
    }

Through Network IPv4 POST route you can create one or more Network IPv4 objects. Only "vlan" field are required. You can specify other fields such as:

* **oct1**, **oct2**, **oct3**, **oct4** - Are the octets of Network IPv4. Given an Vlan, API can provide automatically a Network IPv4 range to you, but it's possible to assign a Network IPv4 range respecting limits defined in Vlan. If you specify some octet, you need to specify all the others.
* **mask_oct1**, **mask_oct2**, **mask_oct3**, **mask_oct4** and **prefix** - If you specify octets of Network IPv4, it' mandatory to specify the mask by octets or by prefix.
* **network_type** - Says if it's a valid/invalid network of Vip Requests, Equipments or NAT.
* **environmentvip** - Use it to associate a new Network IPv4 to an existent Environment Vip

At the end of POST request, it will be returned the identifiers of new Network IPv4 objects created.

Response Body:

.. code-block:: json

    [
        {
            "id": <integer>
        },...
    ]

Response Example for two Network IPv4 objects created:

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

    /api/v3/networkv4/

