Environment associations
########################

Add or remove environment associations for an existing Peer Group.

POST URL::

    /api/v4/peer-group/{peer_group_id}/environment

DELETE URL::

    /api/v4/peer-group/{peer_group_id}/environment/{environment_id}

The trailing slash is optional. Both endpoints require the Peer Group
management write permission.

POST request body:

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

Removes the association identified by the URL's ``environment_id``. Other environment associations are preserved. The request
returns HTTP 200 with an empty object::

    {}

A Peer Group or association that does not exist returns HTTP 404.
