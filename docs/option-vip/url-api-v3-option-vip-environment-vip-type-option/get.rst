GET
###

Obtaining options vip through environment vip and type option
*************************************************************

URL::

    /api/v3/option-vip/environment-vip/<environment_vip_id>/type-option/<type_option>/

where **environment_vip_id** is the identifier of environment vip used as an argument to retrieve associated options vip and **type_option** is a string that filter the result by some type option. It' mandatory to assign one and only one identifier for **environment_vip_id** and a string for **type_option**. String **type_option** is not case sensitive.


It is possible to specify in several ways fields desired to be retrieved using the above route through the use of some GET parameters. You are not required to use these parameters, but depending on your needs it can make your requests faster if you are dealing with many objects and you need few fields. The following fields are available for its route (hyperlinked or bold marked fields acts as foreign keys and can be expanded using __basic or __details when using **fields**, **include** or **exclude** GET Parameters. Hyperlinked fields points to its documentation):

    * id
    * tipo_opcao
    * nome_opcao_txt

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

Using **fields** GET parameter
******************************

Through **fields**, you can specify desired fields.

Example with field id::

    fields=id

Example with fields id and tipo_opcao::

    fields=id,tipo_opcao

Using **kind** GET parameter
****************************

The above route also accepts the **kind** GET parameter. Only two values are accepted by **kind**: *basic* or *details*. For each value it has a set of default fields. The difference between them is that in general *details* contains more fields than *basic*, and the common fields between them are more detailed for *details*.

Example with basic option::

    kind=basic

Response body with *basic* kind:

.. code-block:: json

    {
        "optionsvip": [{
            "id": <integer>,
            "tipo_opcao": <string>
        },...]
    }

Example with details option::

    kind=details

Response body with *details* kind:

.. code-block:: json

    {
        "optionsvip": [{
            "id": <integer>,
            "tipo_opcao": <string>,
            "nome_opcao_txt": <string>
        },...]
    }


Using **fields** and **kind** together
**************************************

If **fields** is being used together **kind**, only the required fields will be retrieved instead of default.

Example with details kind and id field::

    kind=details&fields=id


Default behavior without **kind** and **fields**
************************************************

If neither **kind** nor **fields** are used in request, the response body will look like this:

Response body:

.. code-block:: json

    {
        "optionsvip": [{
            "id": <integer>,
            "tipo_opcao": <string>
        },...]
    }