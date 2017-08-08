DELETE
######

Deleting a list of Virtual Interface in database
************************************************

Deleting list of equipments and all relationships
=================================================

URL::

    /api/v4/equipment/[equipment_ids]/

where **equipment_ids** are the identifiers of equipments desired to delete. It can use multiple id's separated by semicolons. Doing this, all associations between Equipments and IP addresses, Access, Script (Roteiro), Interface, Environment and Group will be deleted. Equipments that have a relationship at same time between IPv4 and Virtual Interface objects or IPv6 and Virtual Interface objects can't be deleted.

Example with Parameter IDs:

One ID::

    /api/v4/equipment/1/

Many IDs::

    /api/v4/equipment/1;3;8/
