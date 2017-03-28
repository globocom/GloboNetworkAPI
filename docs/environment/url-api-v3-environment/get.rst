GET
###

Obtaining environments
**********************

URL::

    /api/v3/environment/<environment_ids>/

where **environment_ids** are the identifiers of each environment desired to be obtained. To obtain more than one environment, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/environment/1/

Many IDs::

    /api/v3/environment/1;3;8/

Optional GET Parameters::

    details=[integer]

* where:
    * details must receive 1 if desired to receive a more-detailed object response, 0 otherwise.

Response body:

.. code-block:: json

    {
	    "environments": [{
            "id": <integer>,
            "grupo_l3": {
                "id": <integer>,
                "name": <string>
            },
            "ambiente_logico": {
                "id": <integer>,
                "name": <string>
            },
            "divisao_dc": {
                "id": <integer>,
                "name": <string>
            },
            "filter": <integer>,
            "acl_path": <string>,
            "ipv4_template": <string>,
            "ipv6_template": <string>,
            "link": <string>,
            "min_num_vlan_1": <integer>,
            "max_num_vlan_1": <integer>,
            "min_num_vlan_2": <integer>,
            "max_num_vlan_2": <integer>,
            "vrf": <integer>,
            "father_environment": <integer>
        }]
    }


