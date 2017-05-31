GET
###

Obtaining vip requests associated to server pool
************************************************

URL::

    /api/v3/vip-request/pool/<pool_id>/

where **pool_id** is the identifier of the server pool used as an argument to retrieve associated vip requests. Only one **pool_id** can be assigned.

Example::

    /api/v3/vip-request/pool/1/

Response body:

.. code-block:: json

    {
        "url_next_search": "<string>",
        "vips": [{
            "id": <integer>,
            "environmentvip": {
                "id": <integer>,
                "finalidade_txt": <string>,
                "cliente_txt": <string>,
                "ambiente_p44_txt": <string>,
                "description": <string>
            },
            "ipv4": {
                "id": <integer>,
                "ip_formated": <string>,
                "description": <string>
            },
            "ipv6": {
                "id": <integer>,
                "ip_formated": <string>,
                "description": <string>
            },
            "equipments": [{
                "id": <integer>,
                "name": <string>,
                "equipment_type": <string>,
                "model": <string>
            },...],
            "default_names": [
                <string>,...
            ],
            "dscp": <integer>,
            "created": <boolean>
        }],
        "url_prev_search": <string>,
        "prev_search": null ,
        "total": <integer>,
        "next_search": {
            "extends_search": [{
                "viprequestport__viprequestportpool__server_pool": <integer>
            }],
            "end_record": 50,
            "start_record": 25,
            "searchable_columns": [],
            "asorting_cols": [
                "-id"
            ],
            "custom_search": null
        }
    }

* "total" property says how much results would be retrieved. If more than 25 vip request were found, only first 25 results will be retrieved in fact and a URL pointing to next 25 results will come together with response.

