GET
***

Obtaining list of pools with member states updated
**************************************************

URL::

    /api/v3/pool/deploy/<pool_ids>/member/status/

where **pool_ids** are the identifiers of each pool desired to be obtained. To obtain more than one pool, semicolons between the identifiers should be used.

GET Param::

    checkstatus=(0|1)

    To obtain member states **updated**, checkstatus should be assigned to 1. If it is assigned to 0, server pools will be retrieved but the real status of the equipments will not be checked.

Response body:

.. code-block:: json

    {
        "server_pools": [{
            "id": <server_pool_id>,
            "identifier": <string>,
            "default_port": <interger>,
            environmentvip": <environment_id>,
            "servicedownaction": {
                "id": <optionvip_id>,
                "name": <string>
            },
            "lb_method": <string>,
            "healthcheck": {
                "identifier": <string>,
                "healthcheck_type": <string>,
                "healthcheck_request": <string>,
                "healthcheck_expect": <string>,
                "destination": <string>
            },
            "default_limit": <interger>,
            "server_pool_members": [{
                "id": <server_pool_member_id>,
                "identifier": <string>,
                "ipv6": {
                    "ip_formated": <ipv6_formated>,
                    "id": <ipv6_id>
                },
                "ip": {
                    "ip_formated": <ipv4_formated>,
                    "id": <ipv4_id>
                },
                "priority": <interger>,
                "equipment": {
                    "id": <interger>,
                    "name": <string>
                },
                "weight": <interger>,
                "limit": <interger>,
                "port_real": <interger>,
                "last_status_update_formated": <string>,
                "member_status": <interger>
            }],
            "pool_created": <boolean>
        },...]
    }

Pool Member
===========
healthcheck+session enable/disable+user up/down(000 - 111 = 0 - 7)

0 0 0
| | \-- user up/user down (forcado a nao receber nem sessoes de persistencia)
| |     1/0 forcar disable do membro no pool (user up/down)
| \---- habilitar/desabilitar membro (session enable/session disable -
|       nao recebe novas sessoes mas honra persistencia)
|       1/0 habilitar/desabilitar membro no pool para novas sessoes (session disable)
\------ status do healthcheck no LB, somente GET, nao e alterado
        por usuario flag ignorada no PUT.
        1/0 status do healthcheck no LB member up/down