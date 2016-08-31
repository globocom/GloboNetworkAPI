GET
***

"""
        ##############
        ## With ids ##
        ##############
        Return server pools by ids or dict
        :url /api/v3/pool/details/<pool_ids>/
        :param pool_ids=<pool_ids>
        :return list of server pool
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": {
                    "id": <environment_id>,
                    "finalidade_txt": <string>,
                    "cliente_txt": <string>,
                    "ambiente_p44_txt": <string>,
                    "description": <string>
                }
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
        :example
        Return pool with id 1 or 2
        /api/v3/pool/details/1;2/

        ###############
        ## With dict ##
        ###############
        Return list of server pool by dict
        :url /api/v3/pool/details/
        :param GET['search']
        {
            'extends_search': [{
                'environment': <environment_id>
            }],
            'start_record': <interger>,
            'custom_search': '<string>',
            'end_record': <interger>,
            'asorting_cols': [<string>,..],
            'searchable_columns': [<string>,..]
        }
        :return list of server pool with property "total"
        {
            "total": <interger>,
            "server_pools": [..]
        }
        :example
        {
            'extends_search': [{
                'environment': 1
            }],
            'start_record': 0,
            'custom_search': 'pool_123',
            'end_record': 25,
            'asorting_cols': ['identifier'],
            'searchable_columns': [
                'identifier',
                'default_port',
                'pool_created',
                'healthcheck__healthcheck_type'
            ]
        }
        """