DELETE
######

Deleting a list of neighbors in database
****************************************

Deleting list of neighbors
==========================

URL::

    /api/v4/neighbor/[neighbor_ids]/

where **neighbor_ids** are the identifiers of neighbors desired to delete. It can use multiple id's separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v4/neighbor/1/

Many IDs::

    /api/v4/neighbor/1;3;8/
