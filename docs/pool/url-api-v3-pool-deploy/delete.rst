DELETE
******

Deleting a list of server pools in equipments
*********************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/

where **pool_ids** are the identifiers of each pool desired to be deleted in equipment and therefore in database. To delete more than one pool in equipment, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/pool/deploy/1/

Many IDs::

    /api/v3/pool/deploy/1;3;8/
