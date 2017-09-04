DELETE
######

.. _url-api-v4-ipv6-delete-delete-list-ipv6s:

Deleting a list of IPv6 objects in database
*******************************************

Deleting list of IPv6 objects and associated Vip Requests and relationships with Equipments and Virtual Interfaces
==================================================================================================================

URL::

    /api/v4/ipv6/[ipv6_ids]/

where **ipv6_ids** are the identifiers of ipv6s desired to delete. It can use multiple id's separated by semicolons. Doing this, all Vip Request associated with IPv6 desired to be deleted will be deleted too. All associations made to equipments will also be deleted. If Virtual Interface is present in some association of IPv6 desired to be deleted to some equipment, the association will not be deleted and therefore the IPv6 will also not be deleted.

Example with Parameter IDs:

One ID::

    /api/v4/ipv6/1/

Many IDs::

    /api/v4/ipv6/1;3;8/
