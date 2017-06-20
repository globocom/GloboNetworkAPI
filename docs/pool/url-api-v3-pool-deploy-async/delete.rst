DELETE
######

Undeploying list of Server Pool asynchronously
**********************************************

URL::

    /api/v3/pool/deploy/async/[pool_ids]/

You can also undeploy Server Pool objects asynchronously. It is only necessary to provide the same as in the respective synchronous request, where **pool_ids** are the identifiers of Server Pool objects desired to be undeployed separated by commas. In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive the identifier of each Server Pool desired to be undeployed in response, but for each Server Pool you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Server Pool objects be undeployed after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example with one identifier::

    /api/v3/pool/deploy/async/

URL Example with one identifier::

    /api/v3/pool/deploy/async/1;3;8/

Response body:

.. code-block:: json

    [
        {
            "task_id": [string with 36 characters]
        },...
    ]

Response Example for Undeploying two Server Pool objects:

.. code-block:: json

    [
        {
            "task_id": "36dc887e-48bf-4c83-b6f5-281b70976a8f"
        },
        {
            "task_id": "17ebd466-0231-4bd0-8f78-54ed20238fa3"
        }
    ]
