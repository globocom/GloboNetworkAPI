# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, \
    EquipamentoError
from networkapi.exception import InvalidValueError, \
    EquipmentGroupsNotAuthorizedError, RequestVipsNotBeenCreatedError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError, \
    HealthcheckExpectError
from networkapi.infrastructure.script_utils import exec_script, ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi, XMLError
from networkapi.ip.models import Ipv6, Ipv6Equipament, Ip, IpEquipamento, \
    IpNotFoundError, IpEquipmentNotFoundError, IpError, IpNotFoundByEquipAndVipError
from networkapi.log import Log
from networkapi.requisicaovips.models import RequisicaoVips, \
    RequisicaoVipsNotFoundError, RequisicaoVipsError, InvalidFinalidadeValueError, \
    InvalidAmbienteValueError, InvalidCacheValueError, InvalidMetodoBalValueError, \
    InvalidPersistenciaValueError, InvalidHealthcheckTypeValueError, \
    InvalidPriorityValueError, InvalidHealthcheckValueError, \
    InvalidTimeoutValueError, InvalidHostNameError, InvalidMaxConValueError, \
    InvalidServicePortValueError, InvalidRealValueError, InvalidBalAtivoValueError, \
    InvalidTransbordoValueError, InvalidClienteValueError
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, \
    is_valid_int_greater_equal_zero_param, clone
from networkapi.ambiente.models import EnvironmentVip


class RequestMaxconResource(RestResource):

    log = Log('RequestMaxconResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat  requests PUT change limit connections to VIP.
        
        URLs: /vip/<id_vip>/maxcon/<maxcon>/
        """
        
        self.log.info("Change limit connections to VIP")
        
        try:
            
            vip_id = kwargs.get('id_vip')
            maxcon = kwargs.get('maxcon')
                        
            # User permission
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT,AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            # Valid Vip ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(u'The vip_id parameter is not a valid value: %s.', vip_id)
                raise InvalidValueError(None)
            
            # Valid Maxcon
            if not is_valid_int_greater_equal_zero_param(maxcon):
                self.log.error(u'The maxcon parameter is not a valid value: %s.', maxcon)
                raise InvalidValueError(None)
            
            # Existing Vip ID
            vip = RequisicaoVips.get_by_pk(vip_id)
            
            with distributedlock(LOCK_VIP % vip_id):
            
                vip_old = clone(vip)
                
                # Vip must be created
                if not vip.vip_criado:
                    self.log.error(u'Maxcon can not be changed because VIP has not yet been created.')
                    raise RequestVipsNotBeenCreatedError(None)
                
                # Vip equipments permission
                if vip.ip is not None:
                    for ip_equipment in vip.ip.ipequipamento_set.all():
                        if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            self.log.error(u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                            raise EquipmentGroupsNotAuthorizedError(None)
                
                if vip.ipv6 is not None:
                    for ip_equipment in vip.ipv6.ipv6equipament_set.all():
                        if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            self.log.error(u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                            raise EquipmentGroupsNotAuthorizedError(None)
                     
                # Get variables
                variables_map = vip.variables_to_map()
                
                # Valid variables
                vip.set_variables(variables_map)
                
                #Valid real names and real ips of real server
                if variables_map.get('reals') is not None:

                    evip = EnvironmentVip.get_by_values(variables_map.get('finalidade'), variables_map.get('cliente'), variables_map.get('ambiente'))
                    
                    for real in variables_map.get('reals').get('real'):
                        ip_aux_error = real.get('real_ip')
                        equip_aux_error = real.get('real_name')
                        equip = Equipamento.get_by_name(equip_aux_error)

                        #Valid Real
                        RequisicaoVips.valid_real_server(ip_aux_error, equip, evip)
                            
                    # Valid reals_prioritys
                    variables_map, code = vip.valid_values_reals_priority(variables_map)
                    if code is not None:
                        return self.response_error(329)
    
                    # Valid reals_weight
                    variables_map, code = vip.valid_values_reals_weight(variables_map)
                    if code is not None:
                        return self.response_error(330)
                
                    # Valid ports
                    variables_map, code = vip.valid_values_ports(variables_map)
                    if code is not None:
                        return self.response_error(331)
                                    
                
                variables_map['maxcon'] = maxcon
                
                vip.set_variables(variables_map)
                
                vip.save(user, commit = True)
                
                # gerador_vips -i <ID_REQUISICAO> --maxconn
                command =  'gerador_vips -i %d --maxconn' % vip.id
                code, stdout, stderr = exec_script(command)
                
                if code == 0:
                    success_map = dict()
                    success_map['codigo'] = '%04d' % code
                    success_map['descricao'] = {'stdout':stdout, 'stderr':stderr}
        
                    map = dict()
                    map['sucesso'] = success_map
                    return self.response(dumps_networkapi(map))
                else:
                    vip_old.save(user, commit = True)
                    return self.response_error(2, stdout + stderr)
            
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        
        except ScriptError, s:
            return self.response_error(2, s)
        
        except EquipmentGroupsNotAuthorizedError:
            return self.response_error(271)
        
        except RequestVipsNotBeenCreatedError:
            return self.response_error(270,vip_id)
        
        except InvalidValueError, e:
            return self.response_error(332, e.param, e.value)

        except IpNotFoundError:
            return self.response_error(328, ip_aux_error, equip_aux_error)

        except HealthcheckExpectNotFoundError:
            return self.response_error(124)

        except RequisicaoVipsNotFoundError:
            return self.response_error(152)

        except InvalidFinalidadeValueError:
            return self.response_error(125)

        except InvalidClienteValueError:
            return self.response_error(126)

        except InvalidAmbienteValueError:
            return self.response_error(127)

        except InvalidCacheValueError: 
            return self.response_error(128)

        except InvalidMetodoBalValueError: 
            return self.response_error(131)

        except InvalidPersistenciaValueError:
            return self.response_error(132)

        except InvalidHealthcheckTypeValueError:
            return self.response_error(133)
        
        except InvalidPriorityValueError:
            return self.response_error(325)
        
        except EquipamentoNotFoundError, e:
            return self.response_error(326,equip_aux_error)
        
        except IpEquipmentNotFoundError:
            return self.response_error(327,ip_aux_error,equip_aux_error)

        except InvalidHealthcheckValueError:
            return self.response_error(134)

        except InvalidTimeoutValueError:
            return self.response_error(135)

        except InvalidHostNameError: 
            return self.response_error(136)

        except InvalidMaxConValueError: 
            return self.response_error(137)

        except InvalidServicePortValueError, e:
            porta = 'nulo'
            if e.message is not None:
                porta = e.message 
            return self.response_error(138, porta)

        except InvalidRealValueError, e:
            real = 'nulo'
            if e.message is not None:
                real = e.message 
            return self.response_error(151, real)

        except InvalidBalAtivoValueError: 
            return self.response_error(129)

        except InvalidTransbordoValueError, e: 
            transbordo = 'nulo'
            if e.message is not None:
                transbordo = e.message
            return self.response_error(130, transbordo)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except IpNotFoundByEquipAndVipError:
            return self.response_error(334, e.message)

        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError), e:
            return self.response_error(1)