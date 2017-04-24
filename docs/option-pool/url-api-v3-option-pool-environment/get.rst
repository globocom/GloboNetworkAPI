GET
###

Obtaining options pools associated to environment
*************************************************

URL::

    /api/v3/option-pool/environment/<environment_id>/

where **environment_id** is the identifier of the environment used as an argument to retrieve associated option pools. It's mandatory to assign one and only one **environment_id**.

Example::

    /api/v3/option-pool/environment/1/

Response body:

.. code-block:: json

    {
        "options_pool": [{
            "id": <integer>,
            "type": "string",
            "name": "string"
        }, ...]
    }

