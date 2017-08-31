.. _rackdir:

PUT
####


Editing a Rack object
*************************

URL::

    /api/rack/<rack_fk>

Request body:

.. code-block:: json

{
  "rack":
    {
      "config": <boolean>,
      "create_vlan_amb": <boolean>,
      "fabric_id": <integer:fabric_id>,
      "id": <integer:rack_id>,
      "id_ilo": <integer:equipment_id>,
      "id_sw1": <integer:equipment_id>,
      "id_sw2": <integer:equipment_id>,
      "mac_ilo": <string:mac_address>,
      "mac_sw1": <string:mac_address>,
      "mac_sw2": <string:mac_address>,
      "nome": "PUT10",
      "numero": <integer>
    }
}

Request Example:

.. code-block:: json

{
  "rack":
    {
      "config": false,
      "create_vlan_amb": false,
      "fabric_id": 1,
      "id": 10,
      "id_ilo": 3,
      "id_sw1": 1,
      "id_sw2": 2,
      "mac_ilo": "3F:FF:FF:FF:FF:FF",
      "mac_sw1": "1F:FF:FF:FF:FF:FF",
      "mac_sw2": "2F:FF:FF:FF:FF:FF",
      "nome": "PUT10",
      "numero": 10
    }
}

Through PUT route you can update a rack object. These fields are required:

* **id** - It is the fk of the rack.
 **numero** - It is the number of the rack.
 **nome** - It is the name of the rack.

At the end of PUT request, it will be returned the rack object updated.

Response Body:

{
  "rack": {
    "config": false,
    "create_vlan_amb": false,
    "dcroom": 1,
    "id": 10,
    "id_ilo": "OOB-CM-TE01",
    "id_sw1": "LF-CM-TE01-1",
    "id_sw2": "LF-CM-TE01-2",
    "mac_ilo": "3F:FF:FF:FF:FF:FF",
    "mac_sw1": "1F:FF:FF:FF:FF:FF",
    "mac_sw2": "2F:FF:FF:FF:FF:FF",
    "nome": null,
    "numero": null
  }
}