.. _url-api-v4-equipment-port-channel-get:

GET
###

Obtaining a port-channel
************************

Returns a port-channel as retrieved from the running configuration of the
equipment itself by the netconf microservice (the equipment is accessed at
each request).

The route is vendor agnostic: the plugin of the equipment converts the
port-channel number to the name used by the equipment and builds the netconf
filter to retrieve it. Equipments whose plugin does not support getting
port-channels return an error.

URL::

    /api/v4/equipment/[equipment_id]/port-channel/[port_channel]/

where:

* **equipment_id** is the identifier of the equipment.
* **port_channel** is the port-channel number, as registered in NetworkAPI
  (e.g. *1*).

Example::

    /api/v4/equipment/1/port-channel/1/

Response body (``text/plain``)::

    <data>...</data>

The response is the content retrieved by the netconf microservice as is: the
XML of the port-channel retrieved from the equipment, whose structure depends
on the equipment (vendor and model).

Errors
======

======  ==================================================================
Status  Reason
======  ==================================================================
400     Equipment without access or equipment (plugin or model) that does
        not support getting port-channels.
401     Missing or invalid credentials.
403     User without read permission on equipment management.
404     Equipment not found or invalid **port_channel** (not a number).
500     Error connecting to the netconf microservice.
======  ==================================================================

Error responses of the netconf microservice are passed through as is: same
status and body (XML, like
``<error><status>404</status><detail>...</detail></error>``). For example,
404 when the port-channel is not found on the equipment, or 500 when an error
occurs communicating with the equipment.
