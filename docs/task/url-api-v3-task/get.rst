GET
###

How can I know the state of an asynchronous request?
****************************************************

URL::

    /api/v3/task/[task_id]/

where **task_id**  is the generated identifier for some asynchronous task. This route only accepts one **task_id** at a time.

Example with Parameter ID::

    /api/v3/task/f8bb9ecf-ff40-4070-b379-6dcad7c8488a/

A task can assume the five status listed below. One way to track progress of some task is pooling NetworkAPI through this route. Once the task reaches SUCCESS, FAILURE or REVOKED status, you can stop to pooling NetworkAPI because your task have finished:

    * PENDING - The task not yet run or status is unknown.
    * SUCCESS - The task finished successfully.
    * PROGRESS - The task is currently running.
    * FAILURE - The job have failed.
    * REVOKED - The job was cancelled (e.g. For some unknown reason, the worker that was attending the task was killed in a non-graceful way and therefore task was interrupted at the middle).

When task reaches SUCCESS or FAILURE status, you can know the result for your task through the "result" key returned by Task Module.

Response body when PENDING status is returned:

.. code-block:: json

    {
        "status": [string],
        "task_id": [string],
    }

Response body when SUCCESS, PROGRESS, FAILURE or REVOKED status is returned:

.. code-block:: json

    {
        "status": [string],
        "task_id": [string],
        "result": [dict]
    }