PUT
###

Updating list of vlans asynchronously
*************************************

URL::

    /api/v3/vlan/async/

You can also update Vlans asynchronously. It is only necessary to provide the same as in the respective synchronous request (For more information about request body please check :ref:`Synchronous Vlan Updating <url-api-v3-vlan-put-update-list-vlans>`). In this case, when you make request NetworkAPI will create a task to fullfil it. You will not receive the identifier of each Vlan desired to be updated in response, but for each Vlan you will receive an identifier for the created task. Since this is an asynchronous request, it may be that Vlans have been updated after you receive the response. It is your task, therefore, to consult the API through the available means to verify that your request have been met.

URL Example::

    /api/v3/vlan/async/

