DELETE
######

Deleting a list of server pools in database
*******************************************

URL::

    /api/v3/pool/<pool_ids>/

where **pool_ids** are the identifiers of each pool desired to be deleted. To delete more than one pool, semicolons between the identifiers should be used. If at least one pool assigned to **pool_ids** exists in equipment, an exception will be raised.

Example with Parameter IDs:

One ID::

    /api/v3/pool/1/

Many IDs::

    /api/v3/pool/1;3;8/

