PUT
###

.. _url-api-v3-networkv4-put-update-list-networkv4s:

Updating list of Network IPv4 objects in database
*************************************************

URL::

    /api/v3/networkv4/[networkv4_ids]/

where **networkv4_ids** are the identifiers of Network IPv4 objects. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/networkv4/1/

Many IDs::

    /api/v3/networkv4/1;3;8/

Request body:

.. code-block:: json

    {
        "networks": [{
            "id": <integer>,
            "network_type": <integer>,
            "environmentvip": <integer>,
            "cluster-unit": <string>
        },..]
    }

Request Example:

.. code-block:: json

    {
        "networks": [{
            "id": 1,
            "network_type": 2,
            "environmentvip": 2,
            "cluster-unit": ""
        }]
    }

In Network IPv4 PUT request, you can only change cluster-unit, environmentvip and network_type. If you don't provide at your request some of attributes below, this attribute will be changed to Null in database.

* **id** - Identifier of Network IPv4 that will be changed. It's mandatory.
* **network_type** -  Says if it's a valid/invalid network of Vip Requests, Equipments or NAT.
* **environmentvip** - Use it to associate Network IPv4 to an existent Environment Vip.

URL Example::

    /api/v3/networkv4/1/

