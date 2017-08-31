PUT
###

Updating list of equipments in database
***************************************

URL::

/api/v4/equipment/[equipment_ids]/

where **equipment_ids** are the identifiers of equipments. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/equipment/1/

Many IDs::

    /api/v4/equipment/1;3;8/

Request body:

.. code-block:: json

    {
        "equipments": [
            {
                "id": <integer>,
                "environments": [
                    {
                        "id": <integer>,
                        "is_router": <boolean>,
                        "is_controller": <boolean>
                    }, ...
                ],
                "equipment_type": <integer>,
                "groups": [
                    {
                        "id": <integer>
                    }, ...
                ],
                "ipsv4": [
                    {
                        "ipv4": {
                            "id": <integer>
                        },
                        "virtual_interface": {
                            "id": <integer>
                        }
                    }, ...
                ],
                "ipsv6": [
                    {
                        "ipv6": {
                            "id": <integer>
                        },
                        "virtual_interface": {
                            "id": <integer>
                        }
                    }, ...
                ],
                "maintenance": <boolean>,
                "model": <integer>,
                "name": <string>,
                "id_as": <integer>
            }, ...
        ]
    }

* **id** - Specify what Equipment you want to change.
* **environments** - You can associate environments to new Equipment and specify if your equipment in each association will act as a router for specific environment and if it will act as a SDN controller in this particular environment.
* **equipment_type** - You must specify if your Equipment is a Switch, a Router, a Load Balancer...
* **groups** - You can associate the new Equipment to one or more groups of Equipments.
* **ipsv4** - You can assign to the new Equipment how many IPv4 addresses are needed and for each association between IPv4 and Equipment you can set a Virtual Interface.
* **ipsv6** - You can assign to the new Equipment how many IPv6 addresses are needed and for each association between IPv6 and Equipment you can set a Virtual Interface.
* **maintenance** - You must assign to the new Equipment a flag saying if the Equipment is or not in maintenance mode.
* **model** - You must assign to the Equipment some model (Cisco, Dell, HP, F5, ...).
* **name** - You must assign to the Equipment any name.
* **id_as** - You can associate the Equipment with one ASN.

Remember that if you don't provide the not mandatory fields, actual information (e.g. associations between Equipment and Environments) will be deleted. The effect of PUT Request is always to replace actual data by what you provide into fields in this type of request.

URL Example::

    /api/v4/equipment/1/
