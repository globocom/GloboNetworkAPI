DELETE
######

Deleting a list of vip request in database
******************************************

Deleting list of vip-request and associated IP's
================================================

URL::

    /api/v3/vip-request/[vip_request_ids]/

where **vip_request_ids** are the identifiers of vip requests desired to delete. It can use multiple id's separated by semicolons. Doing this, the IP associated with each server pool desired to be deleted will also be deleted if this IP is not associated with any other vip request not contained in list of vip request that the user want to delete.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/1/

Many IDs::

    /api/v3/vip-request/1;3;8/

Deleting list of vip-request keeping associated IP's
====================================================

If desired to delete some vip-request keeping it's associated IP's, you must use an additional parameter in URL.

GET Param::

    keepip=[0|1]

where:

* 1 - Keep IP in database
* 0 - Delete IP in database when it hasn't other relationship (the same as not use keepip parameter)

URL Examples::

    /api/v3/vip-request/1/

With keepip parameter assigned to 1::

    /api/v3/vip-request/1/?keepip=1

