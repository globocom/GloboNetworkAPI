POST
####

Creating list of Virtual Interfaces
***********************************

URL::

    /api/v4/virtual-interface/

Request body:

.. code-block:: json

    {
        "virtual_interfaces": [
            {
                "vrf": <integer>,
                "name": <string>
            }, ...
        ]
    }

* **vrf** - You must associate one Vrf to each new Virtual Interface.
* **name** - You must assign a name to the new Virtual Interface.

URL Example::

    /api/v4/virtual-interface/
