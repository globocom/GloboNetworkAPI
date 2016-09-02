POST
####

Creating list of pools in equipments
************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/

where **pool_ids** are the identifiers of each pool desired to be deployed. These pools must exist in database. To deploy more than one pool, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

/api/v3/pool/1/

Many IDs::

/api/v3/pool/1;3;8/
