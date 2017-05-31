DELETE
######

.. _url-api-v3-vrf-delete-delete-list-vrfs:

Deleting a list of Vrf objects in database
******************************************

Deleting list of Vrf objects and relationships with Equipments
==============================================================

URL::

    /api/v3/vrf/[vrf_ids]/

where **vrf_ids** are the identifiers of Vrf's desired to delete. It can use multiple id's separated by semicolons. Doing this, all associations made to equipments will also be deleted. You can't delete Vrf if it's used at some Environment or have relationship with Vlan and Equipment at same time.

Example with Parameter IDs:

One ID::

    /api/v3/vrf/1/

Many IDs::

    /api/v3/vrf/1;3;8/

