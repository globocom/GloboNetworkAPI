# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.interface.models import Interface
from networkapi.test import BasicTestCase, me, CodeError, ConsultationTest, me, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.assertions import assert_response_error
from networkapi.test.functions import valid_content, valid_response, string_generator
import httplib


class InterfaceConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/interface/fixtures/initial_data.yaml']
    XML_KEY = "interface"
    ID_VALID = 1
    ID_ALTER_VALID = 2
    ID_REMOVE_VALID = 3
    ID_REMOVE_RELATED = 4
    ID_DISCONNECT_VALID = 7
    ID_FOR_CONNECTION = 5
    EQUIP_VALID = 1
    OBJ = Interface

    INTERFACE_FOR_LIST = "InterfaceForList"
    EQUIP_FOR_LIST = 3

    # Urls
    URL_SAVE = "/interface/"
    URL_ALTER = "/interface/%s/"
    URL_REMOVE = "/interface/%s/"
    URL_GET_BY_ID = "/interface/%s/get/"
    URL_GET_BY_EQUIP_OLD = "/interface/equipamento/%s/"
    URL_GET_BY_EQUIP = "/interface/equipment/%s/"
    URL_LIST_CONNECTIONS_OLD = "/interface/%s/equipamento/%s/"
    URL_LIST_CONNECTIONS = "/interface/%s/equipment/%s/"
    URL_REMOVE_CONNECTION = "/interface/%s/%s/"

    def mock_valid(self):
        mock = {}
        mock['id_equipamento'] = 1
        mock['nome'] = 'mock'
        mock['descricao'] = 'mock'
        mock['protegida'] = '0'
        return mock

    def mock_for_disconnect(self):
        mock = {}
        mock['nome'] = string_generator(10)
        mock['descricao'] = 'mock'
        mock['protegida'] = '0'
        mock["id_ligacao_front"] = self.ID_DISCONNECT_VALID
        return mock

    def valid_attr(self, mock, obj):
        assert str(mock['id_equipamento']) == str(obj['equipamento'])
        assert str(mock['nome']) == str(obj['interface'])
        assert str(mock['descricao']) == str(obj['descricao'])
        assert str(mock['protegida']) == str(obj['protegida'])


class InterfaceGetByIdConsultationTest(InterfaceConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.INTERFACE_NOT_FOUND

    def test_get_by_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_id_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ID %
            self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ID %
            self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()

    def test_get_by_id_empty(self):
        self.get_by_id_empty()


class InterfaceGetByEquipConsultationTest(InterfaceConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_get_by_equip_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP %
            self.EQUIP_VALID)
        valid_response(response)
        content = valid_content(response, "interfaces")
        from_db = Interface.objects.filter(equipamento=self.EQUIP_VALID)
        assert len(content) == len(from_db)

    def test_get_by_equip_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_EQUIP %
            self.EQUIP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equip_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_EQUIP %
            self.EQUIP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equip_old_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.EQUIP_VALID)
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        from_db = Interface.objects.filter(equipamento=self.EQUIP_VALID)
        assert len(content) == len(from_db)

    def test_get_by_equip_old_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.EQUIP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equip_old_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.EQUIP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equip_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP %
            self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_equip_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP %
            self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP %
            self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_old_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_equip_old_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_old_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_old_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equip_old_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIP_OLD %
            self.EMPTY_ATTR)
        self._attr_invalid(response)


class InterfaceTest(InterfaceConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        interface = valid_content(response, self.XML_KEY)

        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            interface['id'])
        valid_response(response)
        interface_from_db = valid_content(response, self.XML_KEY)
        if interface_from_db['protegida'] == 'False':
            interface_from_db['protegida'] = '0'
        elif interface_from_db['protegida'] == 'True':
            interface_from_db['protegida'] = '1'
        self.valid_attr(mock, interface_from_db)

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_valid()
        mock["nome"] = "InterfaceAlterNew"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.ID_ALTER_VALID)
        valid_response(response)
        interface_from_db = valid_content(response, self.XML_KEY)
        assert mock['nome'] == interface_from_db['interface']

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {
                self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {
                self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class InterfaceRemoveTest(InterfaceConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.INTERFACE_NOT_FOUND
    CODE_ERROR_RELATED = CodeError.INTERFACE_RELATED

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID,
            CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID,
            CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_related(self):
        response = self.remove(self.ID_REMOVE_RELATED)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=self.CODE_ERROR_RELATED)

    def test_remove_by_id_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_by_id_negative(self):
        self.remove_negative()

    def test_remove_by_id_letter(self):
        self.remove_letter()

    def test_remove_by_id_zero(self):
        self.remove_zero()

    def test_remove_by_id_empty(self):
        self.remove_empty()


class InterfaceDisconnectTest(InterfaceConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.INTERFACE_NOT_FOUND
    CODE_ERROR_IF_NOT_CONNECTED = CodeError.INTERFACE_NOT_CONNECTED

    def test_disconnect_valid(self):
        # It have to be changed, because the interface must be connected
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, "0"))
        valid_response(response)

    def test_disconnect_not_connected(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_REMOVE_VALID, "0"))
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(
            response,
            codigo=self.CODE_ERROR_IF_NOT_CONNECTED)

    def test_disconnect_no_permission(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_no_permission().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, "0"))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_disconnect_no__write_permission(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_no_write_permission().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, "0"))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_disconnect_id_nonexistent(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_NONEXISTENT, "0"))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.INTERFACE_NOT_FOUND)

    def test_disconnect_id_negative(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.NEGATIVE_ATTR, "0"))
        self._attr_invalid(response)

    def test_disconnect_id_letter(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.LETTER_ATTR, "0"))
        self._attr_invalid(response)

    def test_disconnect_id_zero(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ZERO_ATTR, "0"))
        self._attr_invalid(response)

    def test_disconnect_id_empty(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.EMPTY_ATTR, "0"))
        self._attr_invalid(response)

    def test_disconnect_back_front_letter(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_disconnect_back_front_not_zero_one(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, "3"))
        self._attr_invalid(response)

    def test_disconnect_back_front_empty(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_disconnect_back_front_none(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, self.NONE_ATTR))
        self._attr_invalid(response)

    def test_disconnect_back_front_false(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, 'False'))
        self._attr_invalid(response)

    def test_disconnect_back_front_true(self):
        mock = self.mock_for_disconnect()
        self.alter(self.ID_FOR_CONNECTION, {self.XML_KEY: mock})

        response = self.client_autenticado().delete(
            self.URL_REMOVE_CONNECTION %
            (self.ID_DISCONNECT_VALID, 'True'))
        self._attr_invalid(response)


class InterfaceListConnectionsTest(InterfaceConfigTest, AttrTest):

    def test_list_conns_valid(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.EQUIP_FOR_LIST))
        valid_response(response)
        valid_content(response, 'interfaces')

    def test_list_conns_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.EQUIP_FOR_LIST))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_conns_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.EQUIP_FOR_LIST))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_conns_interface_inexistent(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (string_generator(15), self.EQUIP_FOR_LIST))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.INTERFACE_NOT_FOUND)

    def test_list_conns_interface_maxsize(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (string_generator(21), self.EQUIP_FOR_LIST))
        self._attr_invalid(response)

    def test_list_conns_interface_minsize(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (string_generator(2), self.EQUIP_FOR_LIST))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.INTERFACE_NOT_FOUND)

    def test_list_conns_interface_empty(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.EMPTY_ATTR, self.EQUIP_FOR_LIST))
        self._attr_invalid(response)

    def test_list_conns_equip_inexistent(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.ID_NONEXISTENT))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_list_conns_equip_letter(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_list_conns_equip_zero(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_list_conns_equip_empty(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_list_conns_equip_none(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.NONE_ATTR))
        self._attr_invalid(response)

    def test_list_conns_equip_negative(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS %
            (self.INTERFACE_FOR_LIST, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_list_conns_old_valid(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.EQUIP_FOR_LIST))
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_list_conns_old_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.EQUIP_FOR_LIST))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_conns_old_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.EQUIP_FOR_LIST))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_conns_old_interface_inexistent(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (string_generator(15), self.EQUIP_FOR_LIST))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.INTERFACE_NOT_FOUND)

    def test_list_conns_old_interface_maxsize(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (string_generator(21), self.EQUIP_FOR_LIST))
        self._attr_invalid(response)

    def test_list_conns_old_interface_minsize(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (string_generator(2), self.EQUIP_FOR_LIST))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.INTERFACE_NOT_FOUND)

    def test_list_conns_old_interface_empty(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.EMPTY_ATTR, self.EQUIP_FOR_LIST))
        self._attr_invalid(response)

    def test_list_conns_old_equip_inexistent(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.ID_NONEXISTENT))
        valid_response(response, httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_list_conns_old_equip_letter(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_list_conns_old_equip_zero(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_list_conns_old_equip_empty(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_list_conns_old_equip_none(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.NONE_ATTR))
        self._attr_invalid(response)

    def test_list_conns_old_equip_negative(self):
        response = self.client_autenticado().get(
            self.URL_LIST_CONNECTIONS_OLD %
            (self.INTERFACE_FOR_LIST, self.NEGATIVE_ATTR))
        self._attr_invalid(response)


class InterfaceAttrEquipamentoTest(InterfaceConfigTest, AttrTest):

    KEY_ATTR = "id_equipamento"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()


class InterfaceAttrNomeTest(InterfaceConfigTest, AttrTest):

    KEY_ATTR = "nome"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(21)
        self.process_save_attr_invalid(mock)

    @me
    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        response = self.save({self.XML_KEY: mock})
        valid_response(response)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(21)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        response = self.save({self.XML_KEY: mock})
        valid_response(response)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class InterfaceAttrProtegidaTest(InterfaceConfigTest, AttrTest):

    KEY_ATTR = "protegida"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class InterfaceAttrDescricaoTest(InterfaceConfigTest, AttrTest):

    KEY_ATTR = "descricao"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        mock = self.mock_valid()
        mock["nome"] = "InterfaceEmpty"
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.save({self.XML_KEY: mock})
        valid_response(response)

    def test_save_none(self):
        mock = self.mock_valid()
        mock["nome"] = "InterfaceNone"
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        mock = self.mock_valid()
        mock["nome"] = string_generator(5)
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

    def test_alter_none(self):
        mock = self.mock_valid()
        mock["nome"] = string_generator(5)
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)


class InterfaceAttrLigacaoFrontTest(InterfaceConfigTest, AttrTest):

    KEY_ATTR = "id_ligacao_front"
    CODE_ERROR_NOT_FOUND = CodeError.INTERFACE_FRONT_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_ALTER_VALID)

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ID_ALTER_VALID)


class InterfaceAttrLigacaoBackTest(InterfaceConfigTest, AttrTest):

    KEY_ATTR = "id_ligacao_back"
    CODE_ERROR_NOT_FOUND = CodeError.INTERFACE_BACK_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_ALTER_VALID)

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ID_ALTER_VALID)
