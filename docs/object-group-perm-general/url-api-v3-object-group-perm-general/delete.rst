DELETE
######

.. _url-api-v3-object-group-perm-general-delete-delete-list-object-group-perm-generals:

Deleting a list of General Object Group Permissions objects in database
***********************************************************************

Deleting list of General Object Group Permissions objects
=========================================================

URL::

    /api/v3/object-group-perm-general/[object_group_perm_general_ids]/

where **object_group_perm_general_ids** are the identifiers of General Object Group Permissions desired to delete. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/object-group-perm-general/1/

Many IDs::

    /api/v3/object-group-perm-general/1;3;8/

