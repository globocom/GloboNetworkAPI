DELETE
######

Deleting a list of Virtual Interfaces in database
*************************************************

Deleting list of Virtual Interfaces and all relationships
=========================================================

URL::

    /api/v4/equipment/[virtual_interface_ids]/

where **virtual_interface_ids** are the identifiers of Virtual Interfaces desired to delete. It can use multiple id's separated by semicolons. Doing this, all Neighbors that are related to this particular Virtual Interface will be deleted as well as the relationships between Equipments and IPv4's or relationships between Equipments and IPv6's containing this particular Virtual Interface.

Example with Parameter IDs:

One ID::

    /api/v4/equipment/1/

Many IDs::

    /api/v4/equipment/1;3;8/
