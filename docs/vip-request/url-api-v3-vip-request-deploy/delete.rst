DELETE
######

Deleting list of vip requests in equipments
*******************************************

URL::

    /api/v3/vip-request/deploy/[vip_request_ids]/

where **vip_request_ids** are the identifiers of vip requests desired to be deleted. It can use multiple id's separated by semicolons. Doing this, the IP associated with each server pool desired to be deleted will also be deleted if this IP is not associated with any other vip request not contained in list of vip request that the user want to delete.

Example with Parameter IDs:

One ID::

    /api/v3/vip-request/deploy/1/

Many IDs::

    /api/v3/vip-request/deploy/1;3;8/

