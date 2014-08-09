# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.filter.models import Filter
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class FilterConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/ambiente/fixtures/initial_data.yaml']
    XML_KEY = "filter"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    ID_DISSOCIATE_VALID = 4

    # Filter for testing rule of association
    ID_DISSOCIATE_ENV_ASSOCIATED = 8

    # Filters for testing rules of association with environment
    ID_DISSOCIATE_IN_USE_CASE1 = 5
    ID_DISSOCIATE_IN_USE_CASE2 = 6
    ID_DISSOCIATE_IN_USE_CASE3 = 7

    OBJ = Filter

    ID_TYPE_EQUIPMENT = 1

    # Equip type for testing rule of association
    ID_TYPE_EQUIPMENT_ENV_ASSOCIATED = 5

    # Equip types for testing rules of association with environment
    # Note: this may change with the construction of the database fixtures
    ID_TYPE_EQUIPMENT_IN_USE_CASE1 = 2
    ID_TYPE_EQUIPMENT_IN_USE_CASE2 = 3
    ID_TYPE_EQUIPMENT_IN_USE_CASE3 = 4

    # Urls
    URL_SAVE = "/filter/"
    URL_ALTER = "/filter/%s/"
    URL_REMOVE = "/filter/%s/"
    URL_GET_BY_ID = "/filter/get/%s/"
    URL_GET_ALL = "/filter/all/"
    URL_ASSOCIATE = "/filter/%s/equiptype/%s/"
    URL_DISSOCIATE = "/filter/%s/dissociate/%s/"

    def mock_valid(self):
        mock = {}
        mock['name'] = "mock"
        mock['description'] = "mock"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["name"]
        assert mock["description"] == obj["description"]


class FilterConsultationTest(FilterConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.FILTER_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "filter")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, "filter")

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

    def test_get_by_id_empty(self):
        self.get_by_id_empty()


class FilterTest(FilterConfigTest, RemoveTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, "filter")

        response = self.get_by_id(content["id"])
        valid_response(response)
        fil = valid_content(response, "filter")
        self.valid_attr(mock, fil)

        # Remove filter so it does not require cleaning db manually
        response = self.remove(content['id'])
        valid_response(response)

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
        mock["name"] = "FilterAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_by_id(self.ID_ALTER_VALID)
        valid_response(response)
        fil = valid_content(response, "filter")
        self.valid_attr(mock, fil)

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class FilterRemoveTest(FilterConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.FILTER_NOT_FOUND

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


class FilterAttrNameTest(FilterConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        flt = valid_content(response, "filter")

        mock = self.mock_valid()
        mock["name"] = flt["name"]
        self.process_save_attr_invalid(mock, CodeError.FILTER_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_unique(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        flt = valid_content(response, "filter")

        mock = self.mock_valid()
        mock["name"] = flt["name"]
        self.process_alter_attr_invalid(mock, CodeError.FILTER_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class FilterAttrDescriptionTest(FilterConfigTest, AttrTest):

    KEY_ATTR = "description"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.save(mock)

    def test_save_empty(self):
        mock = self.mock_valid()
        mock["name"] = "FilterEmpty"
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_none(self):
        mock = self.mock_valid()
        mock["name"] = "FilterNone"
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response)

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
        mock["name"] = string_generator(5)
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_alter_none(self):
        mock = self.mock_valid()
        mock["name"] = string_generator(5)
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        self._attr_invalid(response)


class FilterAssociateTest(FilterConfigTest, AttrTest):

    def test_associate_valid(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response)
        valid_content(response, "equiptype_filter_xref")

        # Remove filter association so it does not require cleaning db manually
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response)

    def test_associate_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_associate_no__write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_associate_filter_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_NONEXISTENT, self.ID_TYPE_EQUIPMENT))
        self._not_found(response, CodeError.FILTER_NOT_FOUND)

    def test_associate_filter_negative(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.NEGATIVE_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_associate_filter_letter(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.LETTER_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_associate_filter_zero(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ZERO_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_associate_filter_empty(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.EMPTY_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_associate_filter_none(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.NONE_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_associate_type_equipment_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_TYPE_NOT_FOUND)

    def test_associate_type_equipment_negative(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_associate_type_equipment_letter(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_associate_type_equipment_zero(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_associate_type_equipment_empty(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_associate_type_equipment_none(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.NONE_ATTR))
        self._attr_invalid(response)


class FilterDissociateTest(FilterConfigTest, AttrTest):

    def test_dissociate_valid(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response)

    def test_dissociate_cant_because_in_use_case_1(self):
        response = self.client_autenticado().put(self.URL_DISSOCIATE % (
            self.ID_DISSOCIATE_IN_USE_CASE1, self.ID_TYPE_EQUIPMENT_IN_USE_CASE1))
        self._attr_invalid(
            response, CodeError.FILTER_EQUIPTYPE_CANT_DISSOCIATE)

    def test_dissociate_cant_because_in_use_case_2(self):
        response = self.client_autenticado().put(self.URL_DISSOCIATE % (
            self.ID_DISSOCIATE_IN_USE_CASE2, self.ID_TYPE_EQUIPMENT_IN_USE_CASE2))
        self._attr_invalid(
            response, CodeError.FILTER_EQUIPTYPE_CANT_DISSOCIATE)

    def test_dissociate_cant_because_in_use_case_3(self):
        response = self.client_autenticado().put(self.URL_DISSOCIATE % (
            self.ID_DISSOCIATE_IN_USE_CASE3, self.ID_TYPE_EQUIPMENT_IN_USE_CASE3))
        self._attr_invalid(
            response, CodeError.FILTER_EQUIPTYPE_CANT_DISSOCIATE)

    def test_dissociate_valid_associated(self):
        response = self.client_autenticado().put(self.URL_DISSOCIATE % (
            self.ID_DISSOCIATE_ENV_ASSOCIATED, self.ID_TYPE_EQUIPMENT_ENV_ASSOCIATED))
        valid_response(response)

    def test_dissociate_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_dissociate_no__write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.ID_TYPE_EQUIPMENT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_dissociate_filter_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_NONEXISTENT, self.ID_TYPE_EQUIPMENT))
        self._not_found(response, CodeError.FILTER_NOT_FOUND)

    def test_dissociate_filter_negative(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.NEGATIVE_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_dissociate_filter_letter(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.LETTER_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_dissociate_filter_zero(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ZERO_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_dissociate_filter_empty(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.EMPTY_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_dissociate_filter_none(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.NONE_ATTR, self.ID_TYPE_EQUIPMENT))
        self._attr_invalid(response)

    def test_dissociate_type_equipment_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_TYPE_NOT_FOUND)

    def test_dissociate_type_equipment_negative(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_dissociate_type_equipment_letter(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_dissociate_type_equipment_zero(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_dissociate_type_equipment_empty(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_dissociate_type_equipment_none(self):
        response = self.client_autenticado().put(
            self.URL_DISSOCIATE % (self.ID_DISSOCIATE_VALID, self.NONE_ATTR))
        self._attr_invalid(response)
