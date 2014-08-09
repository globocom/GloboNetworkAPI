# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi
from networkapi.interface.models import Interface, InterfaceError, InterfaceNotFoundError, InterfaceInvalidBackFrontError
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.exception import InvalidValueError
from networkapi.distributedlock import distributedlock, LOCK_INTERFACE
from networkapi.util import is_valid_int_greater_zero_param, is_valid_zero_one_param


class InterfaceDisconnectResource(RestResource):

    log = Log('InterfaceDisconnectResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove the connection of two interfaces by front or back

        URL: interface/<id_interface>/<back_or_front>/
        """

        try:

            # Business Validations

            # Valid Interface ID
            id_interface = kwargs.get('id_interface')
            if not is_valid_int_greater_zero_param(id_interface):
                self.log.error(
                    u'The id_interface parameter is not a valid value: %s.', id_interface)
                raise InvalidValueError(None, 'id_interface', id_interface)

            # Valid back or front param
            back_or_front = kwargs.get('back_or_front')
            if not is_valid_zero_one_param(back_or_front):
                self.log.error(
                    u'The back_or_front parameter is not a valid value: %s.', back_or_front)
                raise InvalidValueError(None, 'back_or_front', back_or_front)
            else:
                back_or_front = int(back_or_front)

            # User permission equip 1
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Checks if interface exists in database
            interface_1 = Interface.get_by_pk(id_interface)

            with distributedlock(LOCK_INTERFACE % id_interface):

                # Is valid back or front connection
                if back_or_front:
                    try:
                        interface_2 = Interface.get_by_pk(
                            interface_1.ligacao_front_id)
                    except InterfaceNotFoundError:
                        raise InterfaceInvalidBackFrontError(
                            None, "Interface two has no connection with front of Interface one")
                else:
                    try:
                        interface_2 = Interface.get_by_pk(
                            interface_1.ligacao_back_id)
                    except InterfaceNotFoundError:
                        raise InterfaceInvalidBackFrontError(
                            None, "Interface two has no connection with back of Interface one")

                if interface_2.ligacao_front_id == interface_1.id:
                    back_or_front_2 = 1
                elif interface_2.ligacao_back_id == interface_1.id:
                    back_or_front_2 = 0
                else:
                    raise InterfaceInvalidBackFrontError(
                        None, "Interface one has no connection with front or back of Interface two")

                # Business Rules

                # Remove Interface one connection
                if back_or_front:
                    interface_1.ligacao_front = None
                else:
                    interface_1.ligacao_back = None

                # Remove Interface two connection
                if back_or_front_2:
                    interface_2.ligacao_front = None
                else:
                    interface_2.ligacao_back = None

                # Save
                interface_1.save(user)
                interface_2.save(user)

                # Return None for success
                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except InterfaceInvalidBackFrontError, e:
            return self.response_error(307, e.message)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
