GET
###

Obtaining options vip through environment vip
*********************************************

URL::

    /api/v3/option-vip/environment-vip/<environment_vip_id>

where **environment_vip_id** is the identifier of environment vip used as an argument to retrieve associated options vip. Only one identifier can be assigned.

Example::

    /api/v3/option-vip/environment-vip/1

Response body:

.. code-block:: json

    [
        {
            "option": {
                "id": <integer>,
                "tipo_opcao": <string>,
                "nome_opcao_txt": <string>
            }
        },...
    ]


