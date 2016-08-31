GET
***

"""
        Returns list of pool by environment vip
        :url /api/v3/pool/environment-vip/<environment_vip_id>/
        :param environment_vip_id:<environment_vip_id>
        :return
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
            },..]
        }
        """

 """
        Method to return option vip list by environment id
        Param environment_id: environment id
        Return list of option pool
        """