.. _url-api-v4-equipment-port-channel-get:

GET
###

Obtaining information of a port-channel
***************************************

Returns a port-channel as retrieved from the running configuration of the
equipment itself by the netconf microservice (the equipment is accessed at
each request).

Currently supported only by Juniper QFX equipments (JUNOS plugin), where
port-channels are aggregated ethernet interfaces (``aeN``).

URL::

    /api/v4/equipment/[equipment_id]/port-channel/[port_channel]/

where:

* **equipment_id** is the identifier of the equipment.
* **port_channel** is the port-channel number, as registered in NetworkAPI
  (e.g. *1*), or its name in Junos (e.g. *ae1*).

Example::

    /api/v4/equipment/1/port-channel/1/

Response body:

.. code-block:: json

    {
        "port_channel": {
            "status": "success",
            "data": "<data><configuration><interfaces><interface><name>ae1</name>...</interface></interfaces></configuration></data>"
        }
    }

The **port_channel** is the response of the netconf microservice as is, where
**data** is the XML of the port-channel retrieved from the equipment.

Errors
======

======  ==================================================================
Status  Reason
======  ==================================================================
400     Equipment without access or equipment whose plugin does not
        support getting port-channels.
401     Missing or invalid credentials.
403     User without read permission on equipment management.
404     Equipment not found, invalid **port_channel** or port-channel not
        found on the equipment.
500     Error connecting or communicating with the equipment.
======  ==================================================================
