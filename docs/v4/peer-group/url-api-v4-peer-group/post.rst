POST
####

Creating list of Peer Group's
*********************

URL::

    /api/v4/peer-group/

Request body:

.. code-block:: json

    {
        "peer_groups": [
            {
                "name": <string>,
                "route_map_in": <integer>
                "route_map_out": <integer>
            },...
        ]
    }

* Both **name**, **route_map_in** and **route_map_out** fields are required.

URL Example::

    /api/v4/peer-group/

TODO