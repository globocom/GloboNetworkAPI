DELETE
######

.. _url-api-v3-networkv6-delete-delete-list-networkv6s:

Deleting a list of Network IPv6 objects in database
***************************************************

Deleting list of Network IPv6 objects and associated IPv6 addresses
===================================================================

URL::

    /api/v3/networkv6/[networkv6_ids]/

where **networkv6_ids** are the identifiers of Network IPv6 objects desired to delete. It can use multiple id's separated by semicolons. Doing this, all IP addresses of Network IPv6 desired to be deleted will be also deleted. Remember that you can't delete Network IPv6 in database if it is deployed or if it exists Vip Request using some IP address of this Network IPv6.

Example with Parameter IDs:

One ID::

    /api/v3/networkv6/1/

Many IDs::

    /api/v3/networkv6/1;3;8/

