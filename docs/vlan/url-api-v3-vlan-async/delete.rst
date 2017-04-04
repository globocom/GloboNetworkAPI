DELETE
######

Deleting list of vlans asynchronously
*************************************

URL::

    /api/v3/vlan/async/

You can also delete Vlans asynchronously. It is only necessary to provide the same as in the respective synchronous request (For more information please check :ref:`Synchronous Vlan Deleting <url-api-v3-vlan-delete-delete-list-vlans>`). In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive an empty dict in response as occurs in the synchronous request, but for each Vlan you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Vlans have been updated after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example::

    /api/v3/vlan/async/

