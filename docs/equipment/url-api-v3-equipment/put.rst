PUT
###

Updating list of equipments in database
***************************************

URL::

/api/v3/equipment/[equipment_ids]/

where **equipment_ids** are the identifiers of equipments. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/equipment/1/

Many IDs::

    /api/v3/equipment/1;3;8/

Request body:

.. code-block:: json

    {
        "equipments": [{
            "id": <integer>,
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
        },..]
    }

* **environments** - You can associate environments to new Equipment and specify if your equipment in each association will act as a router for specific environment.
* **equipment_type** - You must specify if your Equipment is a Switch, a Router, a Load Balancer...
* **groups** - You can associate the new Equipment to one or more groups of Equipments.
* **ipv4** - You can assign to the new Equipment how many IPv4 addresses is needed.
* **ipv6** - You can assign to the new Equipment how many IPv6 addresses is needed.
* **maintenance** - You must assign to the new Equipment a flag saying if the Equipment is or not in maintenance mode.
* **model** - You must assign to the Equipment some model (Cisco, Dell, HP, F5, ...).
* **name** - You must assign to the Equipment any name.

Remember that if you don't provide the not mandatory fields, actual information (e.g. associations between Equipment and Environments) will be deleted. The effect of PUT Request is always to replace actual data by what you provide into fields in this type of request.

URL Example::

    /api/v3/equipment/1/

