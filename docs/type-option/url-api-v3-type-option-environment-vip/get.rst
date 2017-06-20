GET
###

Obtaining options vip through environment vip and type option
*************************************************************

URL::

    /api/v3/type-option/environment-vip/<environment_vip_id>/

where **environment_vip_id** are the identifiers of environment vips used as an argument to retrieve associated type options. It can use multiple id's separated by semicolons.

Example::

    /api/v3/type-option/environment-vip/1/

Response body:

.. code-block:: json

    [
        [
            <string>,...
        ],...
    ]


