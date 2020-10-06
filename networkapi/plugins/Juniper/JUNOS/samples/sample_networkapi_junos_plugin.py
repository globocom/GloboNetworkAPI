"""
How to use:

Step 1 - Edit this file variables accordingly:
    host = 'HOSTNAME_OR_IP'
    user = 'SSH_USER_NAME'
    password = 'SSH_USER_PASSWORD'

Step 2 - Go to another terminal and execute the test (for ANY code modification, please restart this step)
    docker exec -it netapi_app python ./manage.py shell
    execfile('networkapi/plugins/Juniper/JUNOS/samples/sample_networkapi_junos_plugin.py')

Step 3 [optional] - Check more logs in networkapi:
    docker exec -it netapi_app tail -f /tmp/networkapi.log

Step 4 - Check result in equipment, exp.:
    ssh SSH_USER@HOSTNAME_OR_IP
    cli
    show interfaces gr-0/0/0
"""

import logging
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS


# Temporary Equipment class
class EquipamentoAcesso:
    def __init__(self, fqdn, user, password):
        self.fqdn = fqdn
        self.user = user
        self.password = password


# Config log messages
log = logging.getLogger(__name__)
log_test_prefix = '[Junos Plugin]'
log.debug('%s Start sample' % log_test_prefix)

# Requirements (args, equipment and plugin)
host = 'HOSTNAME_OR_IP'
user = 'SSH_USER_NAME'
password = 'SSH_USER_PASSWORD'

# Temporary equipment access object (defined above as EquipamentoAcesso)
equipment_access = EquipamentoAcesso(host, user, password)

# NetworkAPI junos plugin object
equip_plugin = JUNOS(equipment_access=equipment_access)

""" OPEN CONNECTION """
log.debug('%s Open connection ...' % log_test_prefix)
equip_plugin.connect()

""" CHECK PRIVILEGES """
log.debug('%s Check privilege ...' % log_test_prefix)
equip_plugin.ensure_privilege_level()

""" EXECUTE CONFIGURATION """
log.debug('%s Execute configuration file...' % log_test_prefix)
# equip_plugin.exec_command(command='set interfaces gr-0/0/0 description "Some description teste3 for gr-0/0/0 at "')
result = equip_plugin.copyScriptFileToConfig(filename="networkapi/plugins/Juniper/JUNOS/samples/sample_command.txt")
log.debug('Result: %s' % result)

""" CLOSE CONNECTION """
log.debug('%s Close connection ...' % log_test_prefix)
equip_plugin.close()
