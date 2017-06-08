POST
####

Creating list of equipments
***************************

URL::

    /api/v3/equipment/

Request body:

.. code-block:: json

    {
        "equipments": [{
            "environments": [
                {
                    "id": <integer:environment_fk>,
                    "is_router": <boolean>
                },...
            ],
            "equipment_type": <integer:equip_type_fk>,
            "groups": [
                {
                    "id": <integer:group_fk>
                },...
            ],
            "ipv4": [
                {
                    "id": <integer:ipv4_fk>
                }
            ],
            "ipv6" [
                {
                    "id": <integer:ipv6_fk>
                }
            ],
            "maintenance": <boolean>,
            "model": <integer:model_fk>,
            "name": <string>
        },...]
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

    /api/v3/equipment/


