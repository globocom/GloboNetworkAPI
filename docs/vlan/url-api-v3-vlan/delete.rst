DELETE
######

.. _url-api-v3-vlan-delete-delete-list-vlans:

Deleting a list of vlan in database
***********************************

Deleting list of vlan and associated Networks and Object Group Permissions
==========================================================================

URL::

    /api/v3/vlan/[vlan_ids]/

where **vlan_ids** are the identifiers of vlans desired to delete. It can use multiple id's separated by semicolons. Doing this, all NetworkIPv4 and NetworkIPv6 associated with Vlan desired to be deleted will be deleted too. All Object Group Permissions will also be deleted.

Example with Parameter IDs:

One ID::

    /api/v3/vlan/1/

Many IDs::

    /api/v3/vlan/1;3;8/

