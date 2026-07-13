DELETE
######

Undeploy interface configuration from equipment
**********************************************

URL::

    /api/v3/interface/[interface_id]/undeploy_config_sync/

where **interface_id** is the identifier of the interface that will have its
configuration removed from the equipment.

This route generates an undeploy configuration file and then applies it to the
target equipment.

Authentication and permission
=============================

* Requires an authenticated user.
* Requires DeployConfig permission.

Response codes
==============

* **200 OK** - Configuration was successfully undeployed.
* **404 Not Found** - Route parameter **interface_id** was not provided.
* **400 Bad Request** - Invalid interface id.

Example
=======

Request::

    DELETE /api/v3/interface/123/undeploy_config_sync/

Success response body example:

.. code-block:: json

    {
        "<deploy_result>": "<value returned by deploy operation>"
    }
