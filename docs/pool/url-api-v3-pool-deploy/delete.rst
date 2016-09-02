DELETE
######

Deleting a list of server pools in equipments
*********************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/

where **pool_ids** are the identifiers of each pool desired to be deleted only in equipment. In database these server pools will not be deleted, but only flag "created" of each server pool will be changed to "false". To delete more than one pool in equipment, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/pool/deploy/1/

Many IDs::

    /api/v3/pool/deploy/1;3;8/

