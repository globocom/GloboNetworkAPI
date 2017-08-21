.. _rackdir:

POST
####


Creating a Rack object
*************************

URL::

    /api/rack/

Request body:

.. code-block:: json

    {
        "rack":{
            "name": <string>,
            "number": <integer>,
            "mac_sw1": <string:mac_address>,
            "mac_sw2": <string:mac_address>,
            "mac_ilo": <string:mac_address>,
            "id_sw1": <integer:equipment_fk>,
            "id_sw2": <integer:equipment_fk>,
            "id_ilo": <integer:equipment_fk>,
            "dcroom": <integer:fabric_fk>
        }
    }

Request Example:

.. code-block:: json

    {
        "rack":{
            "name": "TE01",
            "number": 2,
            "mac_sw1": "1F:FF:FF:FF:FF:FF",
            "mac_sw2": "2F:FF:FF:FF:FF:FF",
            "mac_ilo": "3F:FF:FF:FF:FF:FF",
            "id_sw1": 1,
            "id_sw2": 2,
            "id_ilo": 3,
            "dcroom": 16
        }
    }

* **dcroom** - It is the fk of the Fabric.
 **name** - It is the name of the Rack.
 **number** - It is the number of the Rack.
 **mac_sw[1,2]** - It is the mac address from each switch.
 **id_sw[1,2]** - It is the fk from each switch.

Only fields 'name' and 'number' are required.

At the end of POST request, it will be returned a json with the Rack object created.

Response Body:

.. code-block:: json

    {
        "rack": {
            "config": false,
            "create_vlan_amb": false,
            "dcroom": 16,
            "id": 10,
            "id_ilo": 3,
            "id_sw1": 1,
            "id_sw2": 2,
            "mac_ilo": "3F:FF:FF:FF:FF:FF",
            "mac_sw1": "1F:FF:FF:FF:FF:FF",
            "mac_sw2": "2F:FF:FF:FF:FF:FF",
            "nome": TE01,
            "numero": 2
            }
    }
