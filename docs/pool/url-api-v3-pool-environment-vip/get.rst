GET
###

Obtaining server pools associated to environment vips
*****************************************************

URL::

    /api/v3/pool/environment-vip/<environment_vip_id>/

where **environment_vip_id** is the identifier of the environment vip used as an argument to retrieve associated server pools. It's mandatory to assign one and only one identifier to **environment_vip_id**. The instruction related to use of extra GET parameters (**kind**, **fields**, **include** and **exclude**) is the same as described in `Server Pool GET Module <url-api-v3-pool-get>`. The only difference is that **fields** GET parameter is always initialized by default with 'id' and 'identifier' fields.

Example::

    /api/v3/pool/environment-vip/1/

