GET
###

Obtaining environments associated to environment vip
****************************************************

URL::

    /api/v3/environment/environment-vip/<environment_vip_id>/

where **environment_vip_id** is the identifier of the environment vip used as an argument to retrieve associated environments. Only one **environment_vip_id** can be assigned. The instruction related to use of extra GET parameters (**kind**, **fields**, **include** and **exclude**) and the default response body is the same as described in :ref:`Environment GET Module <url-api-v3-environment-get>`

Example::

    /api/v3/environment/environment-vip/1/

