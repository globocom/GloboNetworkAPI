PUT
###

.. _url-api-v3-vlan-put-update-list-vlans:

Updating list of Vlans in database
**********************************

URL::

    /api/v3/vlan/[vlan_ids]/

where **vlan_ids** are the identifiers of Vlans. It can use multiple ids separated by semicolons.

Example with Parameter IDs:

One ID::

    /api/v3/vlan/1/

Many IDs::

    /api/v3/vlan/1;3;8/

Request body:

.. code-block:: json

    {
        "vlans": [{
            "name": [string],
            "num_vlan": [integer],
            "environment": [environment_id:integer],
            "description": [string],
            "acl_file_name": [string],
            "acl_valida": [boolean],
            "acl_file_name_v6": [string],
            "acl_valida_v6": [boolean],
            "active": [boolean],
            "vrf": [string],
            "acl_draft": [string],
            "acl_draft_v6": [string]
        },..]
    }

Request Example:

.. code-block:: json

    {
        "vlans": [{
            "id": 1,
            "name": "Vlan changed",
            "num_vlan": 4,
            "environment": 2,
            "description": "",
            "acl_file_name": "",
            "acl_valida": false ,
            "acl_file_name_v6": "",
            "acl_valida_v6": false,
            "active": false,
            "vrf": 'VrfBorda',
            "acl_draft": "",
            "acl_draft_v6": ""
        }]
    }

In Vlan PUT request, you need to specify all fields even you don't want to change some of them.

* **id** - Identifier of Vlan that will be changed.
* **name** - As said, it will be Vlan name.
* **num_vlan** - You can specify manually the number of Vlan. However NetworkAPI can create it automatically for you.
* **environment** - You are required to associate Vlan with some environment.
* **acl_file_name** and **acl_file_name_v6** - You can give ACL names for associated NetworkIPv4 and NetworkIPv6.
* **acl_valida** and **acl_valida_v6** - If not specified ACLs will not be validated by default.
* **active** - If not specified, Vlan will be set to not active.
* **vrf** - Define in what VRF Vlan will be placed.
* **acl_draft** and **acl_draft_v6** - String to define acl draft.
* **create_networkv4** and **create_networkv6** - Through these objects you can create NetworkIPv4 or NetworkIPv6 and automatically associate them to created Vlan.
    * **network_type** - You can specify the type of Network that is desired to create, but you are not required to do that.
    * **environmentvip** - You can associate Network with some Environment Vip, but you are not required to do that.
    * **prefix** - You are required to specify the prefix of Network. For NetworkIPv4 it ranges from 0 to 31 and for NetworkIPv6 it ranges from 0 to 127.


URL Example::

    /api/v3/vlan/1/

