GET
###

Obtaining options vip through environment vip and type option
*************************************************************

URL::

    /api/v3/option-vip/environment-vip/<environment_vip_id>/type-option/<type_option>/

where **environment_vip_id** is the identifier of environment vip used as an argument to retrieve associated options vip and **type_option** is a string that filter the result by some type option. Only one identifier can be assigned to **environment_vip_id** and only one type option can be assigned to **type_option**. String **type_option** is not case sensitive.

Example::

    /api/v3/option-vip/environment-vip/1/type-option/balanceamento/

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

