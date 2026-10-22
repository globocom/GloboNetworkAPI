.. _url-api-v4-equipment-port-channel-get:

GET
###

Obtaining information of a port-channel
***************************************

Returns the name, the member interfaces and the configuration of a
port-channel, obtained from the committed configuration of the equipment
itself (the equipment is accessed at each request).

Currently supported only by Juniper QFX equipments (JUNOS plugin), where
port-channels are aggregated ethernet interfaces (``aeN``) and members are the
interfaces configured with ``gigether-options 802.3ad aeN`` or
``ether-options 802.3ad aeN``.

URL::

    /api/v4/equipment/[equipment_id]/port-channel/[port_channel]/

where:

* **equipment_id** is the identifier of the equipment.
* **port_channel** is the port-channel number, as registered in NetworkAPI
  (e.g. *1*), or its name in Junos (e.g. *ae1*).

GET Parameters
==============

* **display** (optional) is the format of the configuration. Accepted values:

  * *text* (default) - curly braces format, like ``show configuration``.
  * *set* - set commands, like ``show configuration | display set``.

Example::

    /api/v4/equipment/1/port-channel/1/?display=set

Response body:

.. code-block:: json

    {
        "port_channel": {
            "name": "ae1",
            "members": ["xe-0/0/1", "xe-0/0/2"],
            "configuration": "set interfaces xe-0/0/1 gigether-options 802.3ad ae1\nset interfaces xe-0/0/2 gigether-options 802.3ad ae1\nset interfaces ae1 mtu 9216\n..."
        }
    }

The **configuration** contains the configuration of the port-channel and of
its member interfaces.

Errors
======

======  ==================================================================
Status  Reason
======  ==================================================================
400     Invalid **display**, equipment without access or equipment whose
        plugin does not support getting port-channels.
401     Missing or invalid credentials.
403     User without read permission on equipment management.
404     Equipment not found, invalid **port_channel** or port-channel not
        found on the equipment.
500     Error connecting or communicating with the equipment.
======  ==================================================================
