DELETE
######

.. _url-api-v3-object-group-perm-delete-delete-list-object-group-perms:

Deleting a list of Object Group Permissions objects in database
***************************************************************

Deleting list of Object Group Permissions objects
=================================================

URL::

    /api/v3/object-group-perm/[object_group_perm_ids]/

where **object_group_perm_ids** are the identifiers of Object Group Permissions desired to delete. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/object-group-perm/1/

Many IDs::

    /api/v3/object-group-perm/1;3;8/

