POST
####

Deploying list of Network IPv4 asynchronously
*********************************************

URL::

    /api/v3/networkv4/deploy/async/[networkv4_ids]/

You can also deploy Network IPv4 objects asynchronously. It is only necessary to provide the same as in the respective synchronous request, where **networkv4_ids** are the identifiers of Network IPv4 objects desired to be deployed separated by commas. In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive the identifier of each Network IPv4 desired to be deployed in response, but for each Network IPv4 you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Network IPv4 objects be deployed after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example with one identifier::

    /api/v3/networkv4/deploy/async/

URL Example with one identifier::

    /api/v3/networkv4/deploy/async/1;3;8/

Response body:

.. code-block:: json

    [
        {
            "task_id": [string with 36 characters]
        },...
    ]

Response Example for Deploying two Network IPv4 objects:

.. code-block:: json

    [
        {
            "task_id": "36dc887e-48bf-4c83-b6f5-281b70976a8f"
        },
        {
            "task_id": "17ebd466-0231-4bd0-8f78-54ed20238fa3"
        }
    ]
