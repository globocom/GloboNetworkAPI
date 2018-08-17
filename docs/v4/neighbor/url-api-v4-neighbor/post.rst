POST
####

Creating list of Neighbors
**************************

URL::

    /api/v4/neighbor/

Request body:

.. code-block:: json

    {
        "neighbors": [
            {
                "id": <integer>,
                "local_asn": <integer>,
                "local_ip": <integer>,
                "remote_asn": <integer>,
                "remote_ip": <integer>,
                "peer_group": <integer>,
                "community": <boolean>,
                "soft_reconfiguration": <boolean>,
                "remove_private_as": <boolean>,
                "next_hop_self": <boolean>,
                "password": <string>,
                "maximum_hops": <string>,
                "timer_keepalive": <string>,
                "timer_timeout": <string>,
                "description": <string>,
                "kind": <string>,
                "virtual_interface": <integer:virtual_interface_fk>
            }, ...
        ]
    }

* **virtual_interface** - You can associate a virtual interface to new Neighbor passing its identifier in this field.

URL Example::

    /api/v4/neighbor/
