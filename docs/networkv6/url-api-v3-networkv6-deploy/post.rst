POST
####

Deploying list of Network IPv6 in equipments
********************************************

URL::

    /api/v3/networkv6/deploy/[networkv6_ids]/

where **networkv6_ids** are the identifiers of Network IPv6 desired to be deployed. These selected Network IPv6 objects must exist in the database. **networkv6_ids** can also be assigned to multiple id's separated by semicolons.

Examples:

One ID::

    /api/v3/networkv6/deploy/1/

Many IDs::

    /api/v3/networkv6/deploy/1;3;8/
