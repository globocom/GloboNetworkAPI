DELETE
######

.. _url-api-v3-ipv4-delete-delete-list-ipv4s:

Deleting a list of IPv4 objects in database
*******************************************

Deleting list of IPv4 objects and associated Vip Requests and relationships with Equipments
===========================================================================================

URL::

    /api/v3/ipv4/[ipv4_ids]/

where **ipv4_ids** are the identifiers of ipv4s desired to delete. It can use multiple id's separated by semicolons. Doing this, all Vip Request associated with IPv4 desired to be deleted will be deleted too. All associations made to equipments will also be deleted.

Example with Parameter IDs:

One ID::

    /api/v3/ipv4/1/

Many IDs::

    /api/v3/ipv4/1;3;8/

