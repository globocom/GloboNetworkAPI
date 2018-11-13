POST
####

Creating list of equipments
***************************

URL::

    /api/v4/equipment/

Request body:

.. code-block:: json

    {
        "equipments": [
            {
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
                "asn": <integer>
            }, ...
        ]
    }

* **environments** - You can associate environments to new Equipment and specify if your equipment in each association will act as a router for specific environment.
* **equipment_type** - You must specify if your Equipment is a Switch, a Router, a Load Balancer...
* **groups** - You can associate the new Equipment to one or more groups of Equipments.
* **ipv4** - You can assign to the new Equipment how many IPv4 addresses is needed.
* **ipv6** - You can assign to the new Equipment how many IPv6 addresses is needed.
* **maintenance** - You must assign to the new Equipment a flag saying if the Equipment is or not in maintenance mode.
* **model** - You must assign to the Equipment some model (Cisco, Dell, HP, F5, ...).
* **name** - You must assign to the Equipment any name.

URL Example::

    /api/v4/equipment/
