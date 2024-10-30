"""
Interface validator module
"""
import re
import logging
from networkapi.api_rest.exceptions import NetworkAPIException

log = logging.getLogger(__name__)


class InterfaceOverrideValidator:
    """
    Class responsible to interfaces (or ports) valitions.
    """

    def check_overriding(self, source_interface_str_list, target_interface_str_list):
        """
        Public method to check if source interface overides target interfaces. 
        
        Allowed interfaces sample:
        source_interface_str_list = ['eth1/1', 'eth3/2']
        target_interface_str_list = ['eth2', 'eth3/1']

        Prohibited interfaces sample:
        source_interface_str_list = ['eth1/1', 'eth3/2']
        target_interface_str_list = ['eth1', 'eth1/1', 'eth3']

        :param source_interface_str_list str list: String array of interfaces, ex.: ['eth1', 'eth2', 'eth2/1']
        :param target_interface_str_list str list: String array of interfaces, ex.: ['eth2/1/3', 'eth2/1/2/1']
        :return first prohibited interface as False, otherwise, allowed interface as True:
        """

        try:

            log.info('check_overriding START')
            log.info('source_interface_str_list: %s', source_interface_str_list)
            log.info('target_interface_str_list: %s', target_interface_str_list)

            # Validate
            for source_interface_str in source_interface_str_list:
                for target_interface_str in target_interface_str_list:

                    log.info("Validating '%s' with '%s'", source_interface_str, source_interface_str)
                    source_interface_array = [int(num) for num in re.findall(r'\d+', source_interface_str)]
                    target_interface_array = [int(num) for num in re.findall(r'\d+', target_interface_str)]
                    response = self._is_overriding(
                        source_list=source_interface_array,
                        target_list=target_interface_array)
                    if not response:
                        raise NetworkAPIException("A interface requisitada '{}' sobrepoe a interface '{}' do equipamento".format(
                                source_interface_str, target_interface_str
                            )
                        )

        except Exception as ex:
            raise NetworkAPIException(str(ex))

    def _is_overriding(self, source_list, target_list, lvl=0):
        """
        Private method check if source interface overides target interfaces. 
        The interfaces are represented by array, ex. [1,1] is 'eth1/1'.
        
        :param source interfaces: Represented array of interfaces, ex.: [1,1] [1,2,1] [2]
        :param source interfaces: Represented array of interfaces, ex.: [1] [1,2,3] [4]
        :param recursive level control.
        :return first prohibited interface as False, otherwise, allowed interface as True:
        """

        try:
            # Identical
            if source_list == target_list:
                log.info('*** PROHIBITED ***')
                return False
            elif not source_list or not target_list:
                log.info('**** PROHIBITED ****')
                return False
            elif source_list and target_list and source_list[0] == target_list[0]:
                return self._is_overriding(
                    source_list=source_list[1:],
                    target_list=target_list[1:],
                    lvl=lvl+1
                )
            else:
                log.info('**** ALLOWED ****')
                return True
        except Exception as ex:
            raise NetworkAPIException(str(ex))
