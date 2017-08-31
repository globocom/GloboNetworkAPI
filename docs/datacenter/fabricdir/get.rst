.. _fabricdir:

GET
####

Obtaining list of Fabrics
==========================

URL::

    /api/dcrooms/


Get a Fabric by id
===================

URL::

    /api/dcrooms/<fabric_fk>

where **fabric_fk** is the identifier of the fabric desired to be retrieved.


Get a Fabric by the datacenters id
==================================

URL::

    /api/dcrooms/dc/<dc_fk>

where **dc_fk** is the identifier of the datacenter.


Default behavior
=================

The response body will look like this:

Response body:

.. code-block:: json

    {
        "fabric": [{
            "id": 32,
            "name": "POPF",
            "dc": 3,
            "racks": 8,
            "spines": 4,
            "leafs": 2,
            "config": {...}
        },
        ...]
    }