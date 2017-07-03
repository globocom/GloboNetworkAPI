GET
###

Obtaining list of Options Vip
*****************************

It is possible to specify in several ways fields desired to be retrieved in Options Vip module through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for Options Vip module (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * **option**
    * :ref:`environment_vip <url-api-v3-environment-vip-get>`

Obtaining options vip through environment vip
=============================================

URL::

    /api/v3/option-vip/environment-vip/<environment_vip_id>

where **environment_vip_id** is the identifier of environment vip used as an argument to retrieve associated options vip. It's mandatory to assign one and only one identifier to **environment_vip_id**.

Example::

    /api/v3/option-vip/environment-vip/1

Default Response body:

.. code-block:: json

    [
        {
            "option": {
                "id": <integer>,
                "tipo_opcao": <string>,
                "nome_opcao_txt": <string>
            },
            "environment-vip": <integer>
        },...
    ]


