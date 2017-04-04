POST
####

Creating list of vlans asynchronously
*************************************

URL::

    /api/v3/vlan/async/

You can also create Vlans asynchronously. It is only necessary to provide the same as in the respective synchronous request (For more information about request body please check :ref:`Synchronous Vlan Creating <url-api-v3-vlan-post-create-list-vlans>`). In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive the identifier of each Vlan desired to be created in response, but for each Vlan you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Vlans have been created after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example::

    /api/v3/vlan/async/

Response body:

.. code-block:: json

    [
        {
            "task_id": [string with 36 characters]
        },...
    ]

Response Example for update of two Vlans:

.. code-block:: json

    [
        {
            "task_id": "36dc887e-48bf-4c83-b6f5-281b70976a8f"
        },
        {
            "task_id": "17ebd466-0231-4bd0-8f78-54ed20238fa3"
        }
    ]
