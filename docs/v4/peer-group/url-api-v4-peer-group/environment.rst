Environment associations
########################

Add or remove environment associations for an existing Peer Group.

URL::

    /api/v4/peer-group/{peer_group_id}/environment

The trailing slash is optional. The endpoint requires the Peer Group
management write permission.

Request body for both methods:

.. code-block:: json

    {
        "environments_ids": [1, 2]
    }

The list must contain at least one environment ID.

POST
****

Adds the listed environments to the Peer Group. Existing associations are
preserved. The request returns HTTP 201 and the IDs of the created association
records::

    [
        {"id": 10},
        {"id": 11}
    ]

A Peer Group that does not exist returns HTTP 404.

DELETE
******

Removes only the associations matching the listed environment IDs. Other
environment associations are preserved. The request returns HTTP 200 with an
empty object::

    {}

A Peer Group or association that does not exist returns HTTP 404.
