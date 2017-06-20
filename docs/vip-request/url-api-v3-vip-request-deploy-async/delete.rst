DELETE
######

Undeploying list of Vip Request asynchronously
**********************************************

URL::

    /api/v3/vip-request/deploy/async/[vip_request_ids]/

You can also undeploy Vip Request objects asynchronously. It is only necessary to provide the same as in the respective synchronous request, where **vip_request_ids** are the identifiers of Vip Request objects desired to be undeployed separated by commas. In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive the identifier of each Vip Request desired to be undeployed in response, but for each Vip Request you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Vip Request objects be undeployed after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example with one identifier::

    /api/v3/vip-request/deploy/async/

URL Example with one identifier::

    /api/v3/vip-request/deploy/async/1;3;8/

Response body:

.. code-block:: json

    [
        {
            "task_id": [string with 36 characters]
        },...
    ]

Response Example for Undeploying two Vip Request objects:

.. code-block:: json

    [
        {
            "task_id": "36dc887e-48bf-4c83-b6f5-281b70976a8f"
        },
        {
            "task_id": "17ebd466-0231-4bd0-8f78-54ed20238fa3"
        }
    ]
