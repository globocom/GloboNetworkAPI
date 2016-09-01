DELETE
######

Deleting a list of vip request in database
******************************************

Deleting list of vip-request and associated ip's
================================================

URL::

    /api/v3/vip-request/[vip_request_ids]/

where **vip_request_ids** is the identifier of vip request. It can use multiple id's separated by semicolons. Doing this, the ip associated with each server pool desired to be deleted will also be deleted if this ip is not associated with any other vip request not contained in list of vip request that the user want to delete.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/1/

Many IDs::

    /api/v3/vip-request/1;3;8/

Deleting list of vip-request keeping associated ip's
====================================================

If you want to delete some vip-request keeping it's associated ip's, you must use an additional parameter in URL.

GET Param::

    keepip = [0|1]
    keepip = [0|1 - optional]

where:

1 - Keep ip in database
0 - Delete ip in database when it hasn't other relationship (the same as not use this parameter)

URL Examples::

    /api/v3/vip-request/1/

With keepip parameter::

    /api/v3/vip-request/1/?keepip=[0|1]

