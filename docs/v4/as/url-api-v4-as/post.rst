POST
####

Creating list of AS's
*********************

URL::

    /api/v4/as/

Request body:

.. code-block:: json

    {
        "asns": [
            {
                "name": <string>,
                "description": <string>
            },...
        ]
    }

* Both **name** and **description** fields are required.

URL Example::

    /api/v4/as/
