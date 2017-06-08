GET
###

Obtaining vip requests associated to server pool
************************************************

URL::

    /api/v3/vip-request/pool/<pool_id>/

where **pool_id** is the identifier of the server pool used as an argument to retrieve associated vip requests. Only one **pool_id** can be assigned. The instruction related to use of extra GET parameters (**kind**, **fields**, **include** and **exclude**) and the default response body is the same as described in :ref:`Vip Request GET Module <url-api-v3-vip-request-get>`

Example::

    /api/v3/vip-request/pool/1/

