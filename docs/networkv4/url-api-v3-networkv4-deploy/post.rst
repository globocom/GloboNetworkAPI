POST
####

Deploying list of Network IPv4 in equipments
********************************************

URL::

    /api/v3/networkv4/deploy/[networkv4_ids]/

where **networkv4_ids** are the identifiers of Network IPv4 desired to be deployed. These selected Network IPv4 objects must exist in the database. **networkv4_ids** can also be assigned to multiple id's separated by semicolons.

Examples:

One ID::

    /api/v3/networkv4/deploy/1/

Many IDs::

    /api/v3/networkv4/deploy/1;3;8/
