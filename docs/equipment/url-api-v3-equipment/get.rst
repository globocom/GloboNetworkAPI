GET
###

Obtaining equipments
********************

URL::

    /api/v3/equipment/

Optional GET Parameter::

    rights_write=[string]
    environment=[string]
    ipv4=[string]
    ipv6=[string]
    is_router=[string]
    name=[string]

where **rights_write**, **environment**, **ipv4**, **ipv6**, **is_router** and **name** are characteristics of equipments. These arguments are not case sensitive. Don't forget to encode URL.

Example:

With name and ipv4 GET Parameter::

    /api/v3/equipment/?name=CISCO&ipv4=192.168.0.1

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

* "total" property says how much results would be retrieved. If more than 25 equipments are registered, only first 25 results will be retrieved in fact and a URL pointing to next 25 results will come together with response.


