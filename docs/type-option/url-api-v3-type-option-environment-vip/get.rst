GET
###

Obtaining options vip through environment vip and type option
*************************************************************

URL::

    /api/v3/type-option/environment-vip/<environment_vip_id>/

where **environment_vip_id** is the identifier of environment vip used as an argument to retrieve associated type options. Only one identifier can be assigned to **environment_vip_id**.

Example::

    /api/v3/type-option/environment-vip/1/

Response body:

.. code-block:: json

    {

        "optionsvip": [
            [{
                "id": <integer>,
                "tipo_opcao": <string>,
                "nome_opcao_txt": <string>
            },...]
        ]

    }

