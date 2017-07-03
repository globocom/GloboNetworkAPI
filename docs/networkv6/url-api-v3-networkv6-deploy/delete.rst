DELETE
######

Undeploying list of Network IPv6 objects from equipments
********************************************************

URL::

    /api/v3/networkv6/deploy/[networkv6_ids]/

where **networkv6_ids** are the identifiers of Network IPv6 objects desired to be undeployed from equipments. It can use multiple id's separated by semicolons. The undeployed Network IPv6 will continue existing in database as inactive.

Example with Parameter IDs:

One ID::

    /api/v3/networkv6/deploy/1/

Many IDs::

    /api/v3/networkv6/deploy/1;3;8/

