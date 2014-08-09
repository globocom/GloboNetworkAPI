# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.db.models import Q
from networkapi.equipamento.models import Equipamento
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class EquipmentConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/equipamento/fixtures/initial_data.yaml',
                'networkapi/vlan/fixtures/initial_data.yaml']
    XML_KEY = "equipamentos"
    XML_KEY_EQUIPMENT = "equipamento"
    XML_KEY_GROUP = "equipamento_grupo"
    XML_KEY_IP = "ip"

    # PARAMs
    ID_VALID = 1
    ID_ALTER_VALID = 8
    ID_REMOVE_VALID = 4
    EQUIPMENT_NAME_VALID = "Balanceador de Teste"
    ID_ENVIRONMENT_VALID = 1
    ID_EQUIPMENT_TYPE_VALID = 1
    ID_REMOVE_EQUIPMENT_VALID = 5
    ID_REMOVE_GROUP_VALID = 1
    ID_EQUIPMENT_GROUP_VALID = 1
    ID_IPV4_VALID = 10
    ID_IPV6_VALID = 10
    ID_EQUIPMENT_IPV6_VALID = 4
    ID_IPV4_ASSOC_EQUIPMENT_VALID = 2
    ID_IPV6_ASSOC_EQUIPMENT_VALID = 11
    ID_EQUIPMENT_IPV6_ASSOC_VALID = 2
    ID_USER_TEST = 1

    # URLs
    URL_SAVE = "/equipamento/"
    URL_ALTER = "/equipamento/edit/%s/"
    URL_GET_ALL = "/equipamento/list/"
    URL_GET_ALL_2 = "/equipment/all/"
    URL_GET_BY_ID = "/equipamento/id/%s/"
    URL_GET_BY_NAME = "/equipamento/nome/%s/"
    URL_GET_BY_ENVIRONMENT = "/equipamento/tipoequipamento/%s/ambiente/%s/"
    URL_GET_BY_GROUP = "/equipment/group/%s/"
    URL_REMOVE = "/equipamento/%s/"
    URL_REMOVE_EQUIPMENT_GROUP = "/equipamentogrupo/equipamento/%s/egrupo/%s/"
    URL_REMOVE_ASSOC_IPV4 = "/ip/%s/equipamento/%s/"
    URL_REMOVE_ASSOC_IPV6 = "/ipv6/%s/equipment/%s/remove/"
    URL_ADD_ASSOC_IPV4 = "/ip/%s/equipamento/%s/"
    URL_ADD_ASSOC_IPV6 = "/ipv6/%s/equipment/%s/"
    URL_ADD_ASSOC_GROUP = "/equipamentogrupo/"
    URL_ADD_IPV4 = "/ipv4/"
    URL_ADD_IPV6 = "/ipv6/"
    URL_CREATE_IP = "/ip/"
    URL_FIND_EQUIPMENT = "/equipamento/find/"
    URL_GET_REAL_RELATED = '/equipamento/get_real_related/%s/'

    OBJ = Equipamento

    def mock_group_valid(self):
        mock = {}
        mock['id_grupo'] = 12
        mock['id_equipamento'] = 2
        return mock

    def mock_valid(self):
        mock = {}
        mock['id_tipo_equipamento'] = 1
        mock['id_modelo'] = 1
        mock['nome'] = "EquipamentoNovo"
        mock['id_grupo'] = 11
        return mock

    def mock_alter_valid(self):
        mock = {}
        mock['id_equip'] = self.ID_ALTER_VALID
        mock['id_tipo_equipamento'] = 1
        mock['id_modelo'] = 1
        mock['nome'] = "EQUIPAMENTO_NOVO_ALTERADO"
        return mock

    def mock_ip_valid(self):
        mock = {}
        mock['id_vlan'] = 2
        mock['descricao'] = "NovoIP"
        mock['id_equipamento'] = 4
        return mock

    def mock_ipv4_valid(self):
        mock = {}
        mock['id_network_ipv4'] = 2
        mock['description'] = "NovoIPV4"
        mock['id_equipment'] = 2
        return mock

    def mock_ipv6_valid(self):
        mock = {}
        mock['id_network_ipv6'] = 1
        mock['description'] = "NovoIPV6"
        mock['id_equip'] = 5
        return mock

    def mock_to_search(self):
        mock = {}
        mock["start_record"] = 0
        mock["end_record"] = 25
        mock["asorting_cols"] = []
        mock["searchable_columns"] = []
        mock["custom_search"] = ''
        mock["nome"] = None
        mock["exato"] = False
        mock["ambiente"] = None
        mock["tipo_equipamento"] = None
        mock["grupo"] = None
        mock["ip"] = None
        return mock

    def list_all(self, user):
        equips = self.OBJ.objects.raw(
            "SELECT e.* \
              FROM equipamentos e \
               LEFT JOIN equip_do_grupo edg on e.id_equip = edg.id_equip \
               LEFT JOIN grupos_equip ge on edg.id_egrupo = ge.id \
               LEFT JOIN direitos_grupoequip dg on ge.id = dg.id_egrupo \
               LEFT JOIN grupos g on dg.id_ugrupo = g.id \
               LEFT JOIN usuarios_do_grupo udg on g.id = udg.id_grupo \
               LEFT JOIN usuarios u on udg.id_user = u.id_user \
              WHERE u.id_user = %s \
               AND dg.leitura = 1",
            [user]
        )
        return equips

    def search_attr(self, dicts):
        mock = self.mock_to_search()
        for (k, v) in dicts.iteritems():
            mock[k] = v
        response = self.client_autenticado().postXML(
            self.URL_FIND_EQUIPMENT, {self.XML_KEY_EQUIPMENT: mock})
        return response


class EquipmentConsultationTest(EquipmentConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_list_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)
        assert len(content) == len(set(self.list_all(self.ID_USER_TEST)))

    def test_list_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_list_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all(self):
        response = self.client_autenticado().get(self.URL_GET_ALL_2)
        valid_response(response)
        content = valid_content(response, self.XML_KEY, True)
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_ALL_2)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_ALL_2)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_get_by_id_no_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.get_by_id(
            self.ID_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()


class EquipmentConsultationNameTest(EquipmentConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_get_by_name_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_NAME % self.EQUIPMENT_NAME_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_get_by_name_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_NAME % self.EQUIPMENT_NAME_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_name_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_NAME % self.EQUIPMENT_NAME_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_name_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_NAME % string_generator(10))
        self._not_found(response)


class EquipmentConsultationRealRelated(EquipmentConfigTest, ConsultationTest):

    def test_get_real_related_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_REAL_RELATED % self.ID_VALID)
        valid_response(response)

    def test_get_real_related_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_REAL_RELATED % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_real_related_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_REAL_RELATED % self.ID_NONEXISTENT)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_real_related_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_REAL_RELATED % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_get_real_related_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_REAL_RELATED % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_real_related_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_REAL_RELATED % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_real_related_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_REAL_RELATED % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_real_related_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_REAL_RELATED % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EquipmentConsultationEnvironmenTest(EquipmentConfigTest, ConsultationTest):

    def test_get_by_environment_valid(self):
        response = self.client_autenticado().get(self.URL_GET_BY_ENVIRONMENT %
                                                 (self.ID_EQUIPMENT_TYPE_VALID, self.ID_ENVIRONMENT_VALID))
        valid_response(response)

    def test_get_by_environment_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BY_ENVIRONMENT %
                                                   (self.ID_EQUIPMENT_TYPE_VALID, self.ID_ENVIRONMENT_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_BY_ENVIRONMENT %
                                                        (self.ID_EQUIPMENT_TYPE_VALID, self.ID_ENVIRONMENT_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.ID_NONEXISTENT, self.ID_ENVIRONMENT_VALID))
        self._not_found(response, CodeError.EQUIPMENT_TYPE_NOT_FOUND)

    def test_get_by_environment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.NEGATIVE_ATTR, self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_environment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.LETTER_ATTR, self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_environment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.ZERO_ATTR, self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_environment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.EMPTY_ATTR, self.ID_ENVIRONMENT_VALID))
        self._attr_invalid(response)

    def test_get_by_equipment_type_nonexistent(self):
        response = self.client_autenticado().get(self.URL_GET_BY_ENVIRONMENT %
                                                 (self.ID_EQUIPMENT_TYPE_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.ENVIRONMENT_NOT_FOUND)

    def test_get_by_equipment_type_negative(self):
        response = self.client_autenticado().get(self.URL_GET_BY_ENVIRONMENT %
                                                 (self.ID_EQUIPMENT_TYPE_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_get_by_equipment_type_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.ID_EQUIPMENT_TYPE_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_get_by_equipment_type_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.ID_EQUIPMENT_TYPE_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_get_by_equipment_type_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENVIRONMENT % (self.ID_EQUIPMENT_TYPE_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)


class EquipmentConsultationGroupTest(EquipmentConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_NOT_FOUND

    def test_get_by_group_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP % self.ID_EQUIPMENT_GROUP_VALID)
        valid_response(response)

    def test_get_by_group_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_GROUP % self.ID_EQUIPMENT_GROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_group_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_GROUP % self.ID_EQUIPMENT_GROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_group_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_group_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_group_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_group_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_group_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EquipmentRemoveTest(EquipmentConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_negative(self):
        self.remove_negative()

    def test_remove_letter(self):
        self.remove_letter()

    def test_remove_zero(self):
        self.remove_zero()

    def test_remove_empty(self):
        self.remove_empty()


class EquipmentRemoveGroupTest(EquipmentConfigTest, RemoveTest):

    def test_remove_equipment_valid(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_REMOVE_GROUP_VALID))
        valid_response(response)

    def test_remove_equipment_no_permission(self):
        response = self.client_no_permission().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                      (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_REMOVE_GROUP_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_no_write_permission(self):
        response = self.client_no_write_permission().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                            (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_REMOVE_GROUP_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_NONEXISTENT, self.ID_REMOVE_GROUP_VALID))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.NEGATIVE_ATTR, self.ID_REMOVE_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.LETTER_ATTR, self.ID_REMOVE_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_EQUIPMENT_GROUP % (self.ZERO_ATTR, self.ID_REMOVE_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_EQUIPMENT_GROUP % (self.EMPTY_ATTR, self.ID_REMOVE_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_EQUIPMENT_GROUP % (self.NONE_ATTR, self.ID_REMOVE_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_group_nonexistent(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_GROUP_NOT_FOUND)

    def test_remove_group_negative(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_group_letter(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_group_zero(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_group_empty(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_remove_group_none(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_EQUIPMENT_GROUP %
                                                    (self.ID_REMOVE_EQUIPMENT_VALID, self.NONE_ATTR))
        self._attr_invalid(response)


class EquipmentRemoveIpv4AssocTest(EquipmentConfigTest, RemoveTest):

    def test_remove_ip_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.ID_VALID))
        valid_response(response)

    def test_remove_ip_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.ID_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_ip_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.ID_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_ip_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_NONEXISTENT, self.ID_VALID))
        self._not_found(response, CodeError.IP_NOT_FOUND)

    def test_remove_ip_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.NEGATIVE_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_remove_ip_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.LETTER_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_remove_ip_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ZERO_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_remove_ip_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.EMPTY_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_remove_ip_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.NONE_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV4 % (self.ID_IPV4_VALID, self.NONE_ATTR))
        self._attr_invalid(response)


class EquipmentRemoveIpv6AssocTest(EquipmentConfigTest, RemoveTest):

    def test_remove_ip_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.ID_EQUIPMENT_IPV6_VALID))
        valid_response(response)

    def test_remove_ip_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.ID_EQUIPMENT_IPV6_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_ip_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.ID_EQUIPMENT_IPV6_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_ip_nonexistent(self):
        response = self.client_autenticado().delete(self.URL_REMOVE_ASSOC_IPV6 %
                                                    (self.ID_NONEXISTENT, self.ID_EQUIPMENT_IPV6_VALID))
        self._not_found(response, CodeError.IP_NOT_FOUND)

    def test_remove_ip_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.NEGATIVE_ATTR, self.ID_EQUIPMENT_IPV6_VALID))
        self._attr_invalid(response)

    def test_remove_ip_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.LETTER_ATTR, self.ID_EQUIPMENT_IPV6_VALID))
        self._attr_invalid(response)

    def test_remove_ip_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ZERO_ATTR, self.ID_EQUIPMENT_IPV6_VALID))
        self._attr_invalid(response)

    def test_remove_ip_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.EMPTY_ATTR, self.ID_EQUIPMENT_IPV6_VALID))
        self._attr_invalid(response)

    def test_remove_ip_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.NONE_ATTR, self.ID_EQUIPMENT_IPV6_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE_ASSOC_IPV6 % (self.ID_IPV6_VALID, self.NONE_ATTR))
        self._attr_invalid(response)


class EquipmentTestIp(EquipmentConfigTest, RemoveTest):

    def test_save_ipv4_valid(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.ID_VALID))
        valid_response(response)

    def test_save_ipv4_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.ID_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv4_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.ID_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv4_equipment_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_NONEXISTENT, self.ID_VALID))
        self._not_found(response, CodeError.IP_NOT_FOUND)

    def test_save_ipv4_equipment_negative(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.NEGATIVE_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_save_ipv4_equipment_letter(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.LETTER_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_save_ipv4_equipment_zero(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ZERO_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_save_ipv4_equipment_empty(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.EMPTY_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_save_ipv4_equipment_none(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.NONE_ATTR, self.ID_VALID))
        self._attr_invalid(response)

    def test_save_equipment_ipv4_nonexistent(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV4 %
                                                 (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_save_equipment_ipv4_negative(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV4 %
                                                 (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv4_letter(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV4 %
                                                 (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv4_zero(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv4_empty(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv4_none(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV4 % (self.ID_IPV4_ASSOC_EQUIPMENT_VALID, self.NONE_ATTR))
        self._attr_invalid(response)

    def test_save_ipv6_valid(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 % (
            self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        valid_response(response)

    def test_save_ipv6_no_permission(self):
        response = self.client_no_permission().put(self.URL_ADD_ASSOC_IPV6 % (
            self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv6_no_write_permission(self):
        response = self.client_no_write_permission().put(self.URL_ADD_ASSOC_IPV6 % (
            self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_ipv6_equipment_nonexistent(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 %
                                                 (self.ID_NONEXISTENT, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        self._not_found(response, CodeError.IP_NOT_FOUND)

    def test_save_ipv6_equipment_negative(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 %
                                                 (self.NEGATIVE_ATTR, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        self._attr_invalid(response)

    def test_save_ipv6_equipment_letter(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 %
                                                 (self.LETTER_ATTR, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        self._attr_invalid(response)

    def test_save_ipv6_equipment_zero(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV6 % (self.ZERO_ATTR, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        self._attr_invalid(response)

    def test_save_ipv6_equipment_empty(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV6 % (self.EMPTY_ATTR, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        self._attr_invalid(response)

    def test_save_ipv6_equipment_none(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV6 % (self.NONE_ATTR, self.ID_EQUIPMENT_IPV6_ASSOC_VALID))
        self._attr_invalid(response)

    def test_save_equipment_ipv6_nonexistent(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 %
                                                 (self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_save_equipment_ipv6_negative(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 %
                                                 (self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv6_letter(self):
        response = self.client_autenticado().put(self.URL_ADD_ASSOC_IPV6 %
                                                 (self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv6_zero(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV6 % (self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv6_empty(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV6 % (self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_save_equipment_ipv6_none(self):
        response = self.client_autenticado().put(
            self.URL_ADD_ASSOC_IPV6 % (self.ID_IPV6_ASSOC_EQUIPMENT_VALID, self.NONE_ATTR))
        self._attr_invalid(response)


class EquipmentGroupTest(EquipmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_group_valid()
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_GROUP)

    def test_save_no_permission(self):
        mock = self.mock_group_valid()
        response = self.client_no_permission().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_group_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentGroupTestGroup(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_grupo"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)


class EquipmentGroupTestEquipment(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_equipamento"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_group_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_ASSOC_GROUP, {self.XML_KEY_GROUP: mock})
        self._attr_invalid(response)


class EquipmentTest(EquipmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY_EQUIPMENT: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY_EQUIPMENT: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_alter_valid()
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        valid_response(response)

    def test_alter_no_permission(self):
        mock = self.mock_alter_valid()
        response = self.client_no_permission().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_alter_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentTestEquipmentType(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_tipo_equipamento"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_TYPE_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self._attr_nonexistent()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self._attr_negative()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self._attr_letter()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self._attr_zero()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self._attr_empty()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self._attr_none()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_nonexistent(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._not_found(response)

    def test_alter_negative(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_letter(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_zero(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_empty(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_none(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)


class EquipmentTestModel(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_modelo"
    CODE_ERROR_NOT_FOUND = CodeError.MODEL_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self._attr_nonexistent()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self._attr_negative()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self._attr_letter()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self._attr_zero()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self._attr_empty()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self._attr_none()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_nonexistent(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._not_found(response)

    def test_alter_negative(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_letter(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_zero(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_empty(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_none(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)


class EquipmentTestGroup(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_grupo"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self._attr_nonexistent()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self._attr_negative()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self._attr_letter()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self._attr_zero()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self._attr_empty()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self._attr_none()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)


class EquipmentTestName(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "nome"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self._attr_empty()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self._attr_none()
        response = self.save({self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_maxsize(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = string_generator(31)
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_empty(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)

    def test_alter_none(self):
        mock = self.mock_alter_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ALTER % self.ID_ALTER_VALID, {self.XML_KEY_EQUIPMENT: mock})
        self._attr_invalid(response)


class Ipv4Test(EquipmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_ipv4_valid()
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_IP)

    def test_save_no_permission(self):
        mock = self.mock_ipv4_valid()
        response = self.client_no_permission().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_ipv4_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class Ipv4TestIpv4(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_network_ipv4"
    CODE_ERROR_NOT_FOUND = CodeError.NETWORK_IPV4_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class Ipv4TestEquipment(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_equipment"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class Ipv4TestDescription(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "description"

    def test_save_maxsize(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_minsize(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ipv4_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV4, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class Ipv6Test(EquipmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_ipv6_valid()
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_IP)

    def test_save_no_permission(self):
        mock = self.mock_ipv6_valid()
        response = self.client_no_permission().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_ipv6_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class Ipv6TestIpv6(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_network_ipv6"
    CODE_ERROR_NOT_FOUND = CodeError.NETWORK_IPV6_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class Ipv6TestEquipment(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_equip"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class Ipv6TestDescription(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "description"

    def test_save_maxsize(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_minsize(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ipv6_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_ADD_IPV6, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class IpTest(EquipmentConfigTest):

    def test_save_valid(self):
        mock = self.mock_ip_valid()
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_IP)

    def test_save_no_permission(self):
        mock = self.mock_ip_valid()
        response = self.client_no_permission().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_ip_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class IpTestIp(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_vlan"
    CODE_ERROR_NOT_FOUND = CodeError.VLAN_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class IpTestEquipment(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "id_equipamento"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_save_nonexistent(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._not_found(response)

    def test_save_negative(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_letter(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_zero(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)


class IpTestDescription(EquipmentConfigTest, AttrTest):

    KEY_ATTR = "descricao"

    def test_save_maxsize(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_minsize(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        valid_content(response, self.XML_KEY_IP)

    def test_save_none(self):
        mock = self.mock_ip_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_CREATE_IP, {self.XML_KEY_IP: mock})
        valid_content(response, self.XML_KEY_IP)


class EquipmentSearchTest(EquipmentConfigTest):

    def test_search_valid(self):
        mock = self.mock_to_search()
        response = self.client_autenticado().postXML(
            self.URL_FIND_EQUIPMENT, {self.XML_KEY_EQUIPMENT: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_no_permission(self):
        mock = self.mock_to_search()
        response = self.client_no_permission().postXML(
            self.URL_FIND_EQUIPMENT, {self.XML_KEY_EQUIPMENT: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_search_no_read_permission(self):
        mock = self.mock_to_search()
        response = self.client_no_read_permission().postXML(
            self.URL_FIND_EQUIPMENT, {self.XML_KEY_EQUIPMENT: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentSearchAttrsTest(EquipmentConfigTest, AttrTest):

    # Attribute nome

    def test_search_name_valid(self):
        response = self.search_attr({'nome': 'EquipmentForInterface'})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_name_minsize(self):
        response = self.search_attr({'nome': string_generator(2)})
        self._attr_invalid(response)

    # Attribute exato
    def test_search_exact_valid(self):
        response = self.search_attr(
            {'nome': 'EquipmentForInterface', 'exato': '1'})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_exact_invalid(self):
        response = self.search_attr(
            {'nome': 'EquipmentForInterface', 'exato': string_generator(4)})
        self._attr_invalid(response)

    # Attribute ambiente
    def test_search_env_valid(self):
        response = self.search_attr({'ambiente': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_env_letter(self):
        response = self.search_attr({'ambiente': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_env_negative(self):
        response = self.search_attr({'ambiente': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_env_zero(self):
        response = self.search_attr({'ambiente': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Attribute tipo_equipamento
    def test_search_equipment_type_valid(self):
        response = self.search_attr({'tipo_equipamento': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_equipment_type_letter(self):
        response = self.search_attr({'tipo_equipamento': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_equipment_type_negative(self):
        response = self.search_attr({'tipo_equipamento': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_equipment_type_zero(self):
        response = self.search_attr({'tipo_equipamento': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Attribute grupo
    def test_search_group_valid(self):
        response = self.search_attr({'grupo': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_group_letter(self):
        response = self.search_attr({'grupo': self.LETTER_ATTR})
        self._attr_invalid(response)

    def test_search_group_negative(self):
        response = self.search_attr({'grupo': self.NEGATIVE_ATTR})
        self._attr_invalid(response)

    def test_search_group_zero(self):
        response = self.search_attr({'grupo': self.ZERO_ATTR})
        self._attr_invalid(response)

    # Attribute ip
    def test_search_ip_valid(self):
        response = self.search_attr({'ip': '192.168.20.31'})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_ipv6_valid(self):
        response = self.search_attr(
            {'ip': 'ffab:cdef:ffff:ffff:0000:0000:0000:0014'})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_search_ip_letter(self):
        response = self.search_attr({'ip': string_generator(50)})
        self._attr_invalid(response)

    # Attribute composed
    def test_composed_name_environment_valid(self):
        response = self.search_attr(
            {'nome': 'EquipmentForInterface', 'ambiente': 1})
        valid_response(response)
        valid_content(response, self.XML_KEY_EQUIPMENT)

    def test_composed_name_number_letter(self):
        response = self.search_attr(
            {'ambiente': self.LETTER_ATTR, 'nome': 'EquipmentForInterface'})
        self._attr_invalid(response)

    def test_composed_name_minsize_number(self):
        response = self.search_attr(
            {'ambiente': 1, 'nome': string_generator(2)})
        self._attr_invalid(response)
