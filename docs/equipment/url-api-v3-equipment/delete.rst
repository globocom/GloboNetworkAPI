DELETE
######

Deleting a list of equipments in database
*****************************************

Deleting list of equipments and all relationships
=================================================

URL::

    /api/v3/equipment/[equipment_ids]/

where **equipment_ids** are the identifiers of equipments desired to delete. It can use multiple id's separated by semicolons. Doing this, all associations between Equipments and IP addresses, Access, Script (Roteiro), Interface, Environment and Group will be deleted.

Example with Parameter IDs:

One ID::

    /api/v3/equipment/1/

Many IDs::

    /api/v3/equipment/1;3;8/


