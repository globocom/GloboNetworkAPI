DELETE
######

.. _url-api-v3-ipv6-delete-delete-list-ipv6s:

Deleting a list of IPv6 objects in database
*******************************************

Deleting list of IPv6 objects and associated Vip Requests and relationships with Equipments
===========================================================================================

URL::

    /api/v3/ipv6/[ipv6_ids]/

where **ipv6_ids** are the identifiers of ipv6s desired to delete. It can use multiple id's separated by semicolons. Doing this, all Vip Request associated with IPv6 desired to be deleted will be deleted too. All associations made to equipments will also be deleted.

Example with Parameter IDs:

One ID::

    /api/v3/ipv6/1/

Many IDs::

    /api/v3/ipv6/1;3;8/

