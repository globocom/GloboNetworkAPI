PUT
###

Updating list of Virtual Interfaces in database
***********************************************

URL::

    /api/v4/virtual-interface/[virtual_interface_ids]/

where **virtual_interface_ids** are the identifiers of Virtual Interfaces. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/virtual-interface/1/

Many IDs::

    /api/v4/virtual-interface/1;3;8/

Request body:

.. code-block:: json

    {
        "virtual_interfaces": [
            {
                "id": <integer>,
                "vrf": <integer>,
                "name": <string>
            }, ...
        ]
    }

* **id** - It's the identifier of Virtual Interface you want to edit.
* **vrf** - You must set the Vrf field maintaining actual relationship or setting another Vrf.
* **name** - You must give new name (or the same) to existing Virtual Interface.

Remember that if you don't provide the not mandatory fields, actual information (e.g. association between Virtual Interface and Vrf) will be deleted. The effect of PUT Request is always to replace actual data by what you provide into fields in this type of request.

URL Example::

    /api/v4/virtual-interface/1/
