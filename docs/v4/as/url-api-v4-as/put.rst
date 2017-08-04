PUT
###

Updating list of AS's
*********************

URL::

/api/v4/as/[as_ids]/

where **as_ids** are the identifiers of AS's. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/as/1/

Many IDs::

    /api/v4/as/1;3;8/

Request body:

.. code-block:: json

    {
        "asns": [{
            "id": <integer>,
            "name": <string>,
            "description": <string>
        },...]
    }
* **id** field is mandatory. The other fields are not mandatory, but if they don't provided, they will be replaced by Null.

URL Example::

    /api/v4/as/1/
