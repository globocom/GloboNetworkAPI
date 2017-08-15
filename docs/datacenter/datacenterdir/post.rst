.. _datacenterdir:

POST
####

Creating a Data Center object
******************************

URL::

    /api/dc/

Request body:

.. code-block:: json

    {
        "dc": {
        "dcname": <string>,
        "address": <string>
        }
    }

Request Example:

.. code-block:: json

    {
        "dc": {
        "dcname": "POP-SP",
        "address": "SP"
        }
    }

All fields are required:

* **dcname** - It is the name of the Data Center.
 **address** - It is the location of the Data Center.

At the end of POST request, it will be returned a json with the Data Center object created.

Response Body:

.. code-block:: json

    {
        "dc": {
        "id": 1
        "dcname": "POP-SP",
        "address": "SP"
        }
    }
