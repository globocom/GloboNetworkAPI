.. _rackdir:

GET
####


Obtaining list of Racks
************************

URL::

    /api/rack/


Get a list of Racks by the fabric id
=====================================

URL::

    /api/rack/fabric/<fabric_fk>

where **fabric_fk** is the identifier of the fabric.


Get a Rack by id
=================

URL::

    /api/rack/<rack_fk>

where **rack_fk** is the identifier of the Rack desired to be retrieved.


Default behavior
=================

The response body will look like this:

Response body:

.. code-block:: json

    {
        "racks": [{
            "config": false,
            "create_vlan_amb": false,
            "dcroom": 1,
            "id": 10,
            "id_ilo": "OOB-CM-TE01",
            "id_sw1": "LF-CM-TE01-1",
            "id_sw2": "LF-CM-TE01-2",
            "mac_ilo": "3F:FF:FF:FF:FF:10",
            "mac_sw1": "1F:FF:FF:FF:FF:10",
            "mac_sw2": "2F:FF:FF:FF:FF:10",
            "nome": "TE10",
            "numero": 10
            },...
        ]
    }