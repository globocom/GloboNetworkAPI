.. _fabricdir:

POST
####


Creating a Fabric object
*************************

URL::

    /api/dcrooms/

Request body:

.. code-block:: json

    {
        "dcrooms": {
            "dc": <integer:dc_fk>,
            "name": <string>,
            "racks": <integer>,
            "spines": <integer>,
            "leafs": <integer>,
            "config": <dict>
        }
    }

Request Example:

.. code-block:: json

    {
        "dcrooms": {
            "dc": 1,
            "name":"Fabric name",
            "racks": 32,
            "spines": 4,
            "leafs": 2,
            "config": {}
        }
    }

* **dc** - It is the fk of the Data Center.
 **name** - It is the name of the Fabric.
 **racks** - Total number of the racks in a fabric.
 **spines** - Total number of the spines in a fabric.
 **leafs** - Total number of the leafes in a fabric.
 **config** - Json with the father's environments related to the fabric and it's peculiarities.

Only fields 'dc' and 'name' are required.

Example of config json:

.. code-block:: json

    {
      "BGP": {
        "spines": <string: AS Number>,
        "mpls": <string: AS Number>,
        "leafs": <string: AS Number>
      },
      "Gerencia": {
        "telecom": {
          "vlan": <string: Vlan Number>,
          "rede": <string: IPv4 Net>
        }
      },
      "VLT": {
        "id_vlt_lf1": <string: VLT ID Number>,
        "priority_vlt_lf1": <string: VLT priority Number>,
        "priority_vlt_lf2": <string: VLT priority Number>,
        "id_vlt_lf2": <string: VLT ID Number>
      },
      "Ambiente": [
        {
          "id": <integer: env_fk>,
          "details": [
            {
              "name": <string: Name of the new environment - E.g.: BEFE>,
              "min_num_vlan_1": <integer: Minimum number for Vlan>,
              "max_num_vlan_1": <integer: Maximum number for Vlan>,
              "config": [
                {
                  "subnet": <string: IPv4 or IPv6 Net>,
                  "type": <string: v4 or v6>,
                  "mask": <integer: net mask>,
                  "network_type": <integer: net_type_fk>,
                  "new_prefix": <integer: subnet mask>
                },...
              ]
            }, ...
          ]
        },
        {
          "id": <integer: env_fk>,
          "details": []
        },...
        {
          "id": <integer: env_fk>,
          "details": [
            {
              "v4": {
                "new_prefix": <string: subnet mask>
              },
              "v6": {
                "new_prefix": <string: subnet mask>
              }
            }
          ]
        },...
      ],
      "Channel": {
        "channel": <string: Port Channel base Number>
      }
    }


At the end of POST request, it will be returned a json with the Fabric object created.

Response Body:

.. code-block:: json

    {
        "dcrooms": {
            "id": 1
            "dc": 1,
            "name":"Fabric name",
            "racks": 32,
            "spines": 4,
            "leafs": 2,
            "config": {}
        }
    }
