GET
###

Obtaining environment vips through id's
***************************************

URL::

    /api/v3/environment-vip/<environment_ids>/

where **environment_ids** are the identifiers of each environment vip desired to be obtained. To obtain more than one environment vip, semicolons between the identifiers should be used.

Example with Parameter IDs:

One ID::

    /api/v3/environment-vip/1/

Many IDs::

    /api/v3/environment-vip/1;3;8/

Response body:

.. code-block:: json

{
	"environments_vip": [{
		"id": <integer>,
		"finalidade_txt": <string>,
		"cliente_txt": <string>,
		"ambiente_p44_txt": <string>,
		"description": <string>
	}, ...]
}