GET
###

Obtaining environments
**********************

.. TODO Ver o response body

URL::

    /api/v3/environment/<environment_ids>/

where **environment_ids** are the identifiers of each environment desired to be obtained. To obtain more than one environment, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/environment/1/

Many IDs::

    /api/v3/environment/1;3;8/

Response body:

.. code-block:: json

    {
	    "environments": [{
            "id": 33,
            "grupo_l3": {
                "id": 65,
                "name": "BALANCEAMENTO PUBLICACAO"
            },
            "ambiente_logico": {
                "id": 18,
                "name": "PRODUCAO"
            },
            "divisao_dc": {
                "id": 1,
                "name": "BE"
            },
            "filter": null,
            "acl_path": "BE",
            "ipv4_template": null,
            "ipv6_template": null,
            "link": <string>
            "min_num_vlan_1": null,
            "max_num_vlan_1": null,
            "min_num_vlan_2": null,
            "max_num_vlan_2": null,
            "vrf": null,
            "father_environment": null
        }]
    }

