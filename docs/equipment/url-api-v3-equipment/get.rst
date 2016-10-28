GET
###

Obtaining equipments
********************

URL::

    /api/v3/equipment/

Optional GET Parameters::

    rights_write=[string]
    environment=[integer]
    ipv4=[string]
    ipv6=[string]
    is_router=[integer]
    name=[string]

.. TODO ver o que rights_write deve receber

* where:
    * **rights_write** must receive 1 if desired to obtain the equipments where at least one group to which the user logged in is related has write access.
    * **environment** is some environment identifier.
    * **ipv4** and **ipv6** are IP's must receive some valid IP Adresss.
    * **is_router** must receive 1 if only router equipments are desired, 0 if only equipments that is not routers are desired.
    * **name** is a unique string that only one equipment has.

Example:

With NO GET Parameters::

    /api/v3/equipment/

With environment and ipv4 GET Parameter::

    /api/v3/equipment/?ipv4=192.168.0.1&environment=5

Response body:

.. code-block:: json

    {
        "equipments": [{
            "id": <integer>,
            "name": <string>
        }, ...],
        "url_next_search": <string>,
        "url_prev_search": null,
        "prev_search": null,
        "total": <integer>,
        "next_search": {
            "extends_search": [],
            "end_record": 50,
            "start_record": 25,
            "searchable_columns": [],
            "asorting_cols": [
                "-id"
            ],
            "custom_search": null
        }
    }

* "total" property says how much results would be retrieved. If more than 25 equipments are found, only first 25 results will be retrieved in fact and a URL pointing to next 25 results will come together with response.


