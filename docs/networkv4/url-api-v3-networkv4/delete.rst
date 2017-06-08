DELETE
######

.. _url-api-v3-networkv4-delete-delete-list-networkv4s:

Deleting a list of Network IPv4 objects in database
***************************************************

Deleting list of Network IPv4 objects and associated IPv4 addresses
===================================================================

URL::

    /api/v3/networkv4/[networkv4_ids]/

where **networkv4_ids** are the identifiers of Network IPv4 objects desired to delete. It can use multiple id's separated by semicolons. Doing this, all IP addresses of Network IPv4 desired to be deleted will be also deleted. Remember that you can't delete Network IPv4 in database if it is deployed or if it exists Vip Request using some IP address of this Network IPv4.

Example with Parameter IDs:

One ID::

    /api/v3/networkv4/1/

Many IDs::

    /api/v3/networkv4/1;3;8/

