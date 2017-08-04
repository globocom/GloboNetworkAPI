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
                "remote_as": <string>,
                "remote_ip": <string>,
                "password": <string>,
                "maximum_hops": <string>,
                "timer_keepalive": <string>,
                "timer_timeout": <string>,
                "description": <string>,
                "soft_reconfiguration": <boolean>,
                "community": <boolean>,
                "remove_private_as": <boolean>,
                "next_hop_self": <boolean>,
                "kind": <string>,
                "virtual_interface": <integer:virtual_interface_fk>
            },...
        ]
    }

* **virtual_interface** - You can associate a virtual interface to new Neighbor passing its identifier in this field.

URL Example::

    /api/v4/neighbor/
