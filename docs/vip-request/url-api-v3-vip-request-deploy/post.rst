POST
####

Deploying list of vip request in equipments
*******************************************

URL::

    /api/v3/vip-request/deploy/[vip_request_ids]/

where **vip_request_ids** are the identifiers of vip requests desired to be deployed. These selected vip requests must exist in the database. **vip_request_ids** can also be assigned to multiple id's separated by semicolons.

Examples:

One ID::

    /api/v3/vip-request/deploy/1/

Many IDs::

    /api/v3/vip-request/deploy/1;3;8/
