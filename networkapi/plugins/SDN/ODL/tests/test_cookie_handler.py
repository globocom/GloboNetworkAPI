from nose.tools import assert_equal

from networkapi.plugins.SDN.ODL.utils.cookie_handler import CookieHandler
from networkapi.test.test_case import NetworkApiTestCase

class CookieFieldHandlerTestCaseSuccess(NetworkApiTestCase):
    """Class for testing the Cookie Field Handler."""

    def test_get_cookie_returns_ok_1(self):
        """Test if get_cookie method returns right value for 
            ACL id 150000 and operation type 2."""

        assert_equal(CookieHandler.get_cookie(150000, 2),
                     644245631270912)


    def test_get_cookie_returns_ok_2(self):
        """Test if get_cookie method returns right value for 
            ACL id 85434 and operation type 1."""

        assert_equal(CookieHandler.get_cookie(85434, 1),
                     366936504401920)


    def test_get_cookie_returns_ok_3(self):
        """Test if get_cookie method returns right value for 
            ACL id 76535 and operation type 15."""

        assert_equal(CookieHandler.get_cookie(76535, 15),
                     328719348531200)


    def test_get_cookie_returns_ok_4(self):
        """Test if get_cookie method returns right value for 
            ACL id 25194623 and operation type 11."""

        assert_equal(CookieHandler.get_cookie(25194623, 11),
                     108210084772839424)


    def test_get_id_acl_returns_ok_1(self):
        """Test if get_id_acl method returns right value for 
            cookie 644245631270912."""

        cookie = 644245631270912
        assert_equal(CookieHandler.get_id_acl(cookie),
                     150000)

    def test_get_id_acl_returns_ok_2(self):
        """Test if get_id_acl method returns right value for 
            cookie 366936504401920."""

        cookie = 366936504401920
        assert_equal(CookieHandler.get_id_acl(cookie),
                     85434)


    def test_get_id_acl_returns_ok_3(self):
        """Test if get_id_acl method returns right value for 
            cookie 328719348531200."""

        cookie = 328719348531200
        assert_equal(CookieHandler.get_id_acl(cookie),
                     76535)


    def test_get_id_acl_returns_ok_4(self):
        """Test if get_id_acl method returns right value for 
            cookie 108210084772839424."""

        cookie = 108210084772839424
        assert_equal(CookieHandler.get_id_acl(cookie),
                     25194623)


    def test_get_op_type_returns_ok_1(self):
        """Test if get_op_type method returns right value for 
            cookie 644245631270912."""

        cookie = 644245631270912
        assert_equal(CookieHandler.get_op_type(cookie),
                     2)


    def test_get_op_type_returns_ok_2(self):
        """Test if get_op_type method returns right value for 
            cookie 366936504401920."""

        cookie = 366936504401920
        assert_equal(CookieHandler.get_op_type(cookie),
                     1)


    def test_get_op_type_returns_ok_3(self):
        """Test if get_op_type method returns right value for 
            cookie 328719348531200."""

        cookie = 328719348531200
        assert_equal(CookieHandler.get_op_type(cookie),
                     15)


    def test_get_op_type_returns_ok_4(self):
        """Test if get_op_type method returns right value for 
            cookie 108210084772839424."""

        cookie = 108210084772839424
        assert_equal(CookieHandler.get_op_type(cookie),
                     11)
