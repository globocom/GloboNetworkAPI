Creating a new bgp neighbor
############################



#. **Create the Route-maps**


   Post URL::

    /api/v4/bgp/routemap/

   Request body:

   .. code-block:: json

    {
      "route_map": [
        {
          "action": <enum>,
          "action_reconfig": <string>,
          "list_config_bgp": {
            "id": <integer>,
            "config": <string>,
            "name": <string>,
            "type": <enum>
          },
          "order": <integer>,
          "route_map": {
            "id": <integer>,
            "name": <string>
          }
        }
      ]
    }

   * **action:** You must choose between Permit ("P") and Deny ("D")
   * **action_reconfig:**
   * **list_config_bgp:** Basic list_config_bgp object. It must receive the id of an existing list_config_bgp or the variables to create a new list as 'config', 'name' and 'type'.
        * **id** - Id of an existing list.
        * **config** -
        * **name** -
        * **type** - You must choose between ("P"), ("A") and ("C")
   * **order:** Sets the sequential order of the objects in the route-map.
   * **route_map:** Basic route_map object. It must receive the id of an existing route-map or a name to create a new route.
      * **id** - Id of an existing route-map.
      * **name** - Name of the new route-map.


   Json Example::

    {
      "route_map": [
        {
          "action": "P",
          "action_reconfig": "text-l-2",
          "list_config_bgp": {
            "config": "{'conf': 'test_l_2'}",
            "name": "test_l_2",
            "type": "P"
          },
          "order": 5,
          "route_map": {
            "name": "route laura 2"
          }
        }
      ]
    }



#. **Create the neighbor**

   Post URL::

    /api/v4/bgp/neighborv4/

   Request body:

   .. code-block:: json

    {
      "neighbors": [
        {
          "neighbor_local": {
            "asn": {
              "id": <integer>,
              "name": <string>,
              "description": <string>
            },
            "ip": {
              "id": <integer>
            },
            "equipment": {
              "id": <integer>
            }
          },
          "neighbor_remote": {
            "asn": {
              "id": <integer>,
              "name": <string>,
              "description": <string>
            },
            "ip": {
              "id": <integer>
            },
            "equipment": {
              "id": <integer>
            }
          },
          "peer_group": {
            "id": <integer>,
            "name": <string>,
            "route-map": {
              "route-map-in": {
                "id": <integer>
              },
              "route-map-out": {
                "id": <integer>
              }
            },
            "environments": [
              <integer>
            ]
          },
          "community": <Boolean>,
          "soft_reconfiguration": <Boolean>,
          "remove_private_as": <Boolean>,
          "next_hop_self": <Boolean>,
          "kind": <string>
        }
      ]
    }


   * **neighbor_local:** Basic neighbor local object. It must receive the variables 'asn', 'ip' and 'equipment'.
        * **asn** - The local AS number. It must receive the id of an existing AS or the name and description to create a new AS.
            * **id** - Id of an existing AS.
            * **name** - Name of the new AS.
            * **description** - Description of the new AS.
        * **ip** - The ip of the local neighbor.
            * **id** - Id of the existing ip of the local neighbor.
        * **equipment** - The local equipment.
            * **id** - Id of the existing equipment.
   * **neighbor_remote:** Basic neighbor remote object. It must receive the variables 'asn', 'ip' and 'equipment'.
        * **asn** - The remote AS number. It must receive the id of an existing AS or the name to create a new AS.
            * **id** - Id of an existing AS.
            * **name** - Name of the new AS.
        * **ip** - The ip of the remote neighbor.
            * **id** - Id of the existing ip of the remote neighbor.
        * **equipment** - The remote equipment.
            * **id** - Id of the existing equipment.
   * **peer_group:** Basic peer group object. It must receive the id of an existing peer group or a name to create a new peer group.
        * **id** - Id of an existing peer group.
        * **name** - Name of the new peer group.
        * **route-map** - Basic route map object.
            * **route-map-in** - Route map in object.
                * **id** - Id of an existing route map in.
            * **route-map-in** - Route map in object.
                * **id** - Id of an existing route map out.
        * **environments** List of environments ids.
   * **community:** If true, the community attributes are sent to the neighbor.
   * **soft_reconfiguration:** If true, enable the soft reconfiguration inbound.
   * **remove_private_as:** If true, enable the feature remove private AS.
   * **next_hop_self:** If true, enable next hop self.
   * **kind:**


   json Example::

    {
      "neighbors": [
        {
          "neighbor_local": {
            "asn": {
              "name": "13",
              "description": "ASNAME13"
            },
            "ip": {
              "id": 135491
            },
            "equipment": {
              "id": 22
            }
          },
          "neighbor_remote": {
            "asn": {
              "name": "14",
              "description": "ASNAME14"
            },
            "ip": {
              "id": 135492
            },
            "equipment": {
              "id": 23
            }
          },
          "peer_group": {
            "name": "route 6",
            "route-map": {
              "route-map-in": {
                "id": 6
              },
              "route-map-out": {
                "id": 6
              }
            },
            "environments": [
              457
            ]
          },
          "community": true,
          "soft_reconfiguration": true,
          "remove_private_as": false,
          "next_hop_self": true,
          "kind": "I"
        }
      ]
    }

