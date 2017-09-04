DELETE
######

Deleting list of AS's in database
*********************************

Deleting list of AS's
=====================

URL::

    /api/v4/as/[as_ids]/

where **as_ids** are the identifiers of AS's desired to delete. It can use multiple id's separated by semicolons. If AS is associated with some Equipment, it cannot be deleted until this relationship be removed.

Example with Parameter IDs:

One ID::

    /api/v4/as/1/

Many IDs::

    /api/v4/as/1;3;8/
