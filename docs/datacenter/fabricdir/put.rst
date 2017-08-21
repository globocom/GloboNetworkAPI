.. _fabricdir:

PUT
####

Editing a Fabric object
***********************

URL::

    /api/dcrooms/

Request body:

.. code-block:: json

    {
        "dcrooms": {
            "id": <interger:fabric_fk>,
            "dc": <integer:dc_fk>,
            "name": <string>,
            "racks": <integer>,
            "spines": <integer>,
            "leafs": <integer>,
            "config": <dict>
        }
    }

Request Example:

.. code-block:: json

    {
        "dcrooms": {
            "id": 1,
            "dc": 1,
            "name":"Fabric name",
            "racks": 32,
            "spines": 4,
            "leafs": 2,
            "config": {...}
        }
    }

Through Fabric PUT route you can update a object. These fields are required:

* **id** - It is the fk of the Fabric.
 **dc** - It is the fk of the Data Center.
 **name** - It is the name of the Fabric.

At the end of PUT request, it will be returned the Fabric object updated.

Response Body:

    {
        "dcrooms": {
            "id": 1
            "dc": 1,
            "name":"Fabric name",
            "racks": 32,
            "spines": 4,
            "leafs": 2,
            "config": {...}
        }
    }