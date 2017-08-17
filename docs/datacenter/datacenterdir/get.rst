.. _datacenterdir:

GET
###


Obtaining list of Data Centers
********************************

URL::

    /api/dc/


Default behavior
****************

The response body will look like this:

Response body:

.. code-block:: json

    {
        "dc": [{
            "id": <integer>,
            "dcname": <string>,
            "address": <string>,
            "fabric": <list>
        },...]
    }