DELETE
######

Undeploying list of Network IPv4 objects from equipments
********************************************************

URL::

    /api/v3/networkv4/deploy/[networkv4_ids]/

where **networkv4_ids** are the identifiers of Network IPv4 objects desired to be undeployed from equipments. It can use multiple id's separated by semicolons. The undeployed Network IPv4 will continue existing in database as inactive.

Example with Parameter IDs:

One ID::

    /api/v3/networkv4/deploy/1/

Many IDs::

    /api/v3/networkv4/deploy/1;3;8/

