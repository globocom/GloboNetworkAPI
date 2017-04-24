POST
####

.. _url-api-v3-vlan-post-create-list-vlans:

Creating list of vlans
**********************

URL::

    /api/v3/vlan/

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
            "acl_draft_v6": [string],
            "create_networkv4": {
                "network_type": [network_type_id:integer],
                "environmentvip": [environmentvip_id:integer],
                "prefix": [integer]
            },
            "create_networkv6": {
                "network_type": [network_type_id:integer],
                "environmentvip": [environmentvip_id:integer],
                "prefix": [integer]
            }
        },..]
    }

Request Example with only required fields:

.. code-block:: json

    {
        "vlans": [{
            "name": "Vlan for NetworkAPI",
            "environment": 5,
        }]
    }

Request Example with some more fields:

.. code-block:: json

    {
        "vlans": [{
            "name": "Vlan for NetworkAPI",
            "num_vlan": 3,
            "environment": 5,
            "active": True,
            "create_networkv4": {
                "network_type": 6,
                "environmentvip": 2,
                "prefix": 24
            }
        }]
    }

Through Vlan POST route you can create one or more Vlans. Only "name" and "environment" fields are required. You can specify other fields such as:

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

At the end of POST request, it will be returned the identifiers of new Vlans created.

Response Body:

.. code-block:: json

    [
        {
            "id": [integer]
        },...
    ]

Response Example for two Vlans created:

.. code-block:: json

    [
        {
            "id": 10
        },
        {
            "id": 11
        }
    ]

URL Example::

    /api/v3/vlan/

