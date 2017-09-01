PUT
###

Updating list of neighbors in database
**************************************

URL::

/api/v4/neighbor/[neighbor_ids]/

where **neighbor_ids** are the identifiers of neighbors. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/neighbor/1/

Many IDs::

    /api/v4/neighbor/1;3;8/

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
            }, ...
        ]
    }

* **virtual_interface** - You can associate a virtual interface to new Neighbor passing its identifier in this field.

Remember that if you don't provide the not mandatory fields, actual information (e.g. association to Virtual Interface) will be deleted. The effect of PUT Request is always to replace actual data by what you provide into fields in this type of request.

URL Example::

    /api/v4/neighbor/1/
