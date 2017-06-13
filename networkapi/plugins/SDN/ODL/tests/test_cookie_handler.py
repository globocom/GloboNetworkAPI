from nose.tools import assert_equal

from networkapi.plugins.SDN.ODL.utils.cookie_handler import CookieHandler
from networkapi.test.test_case import NetworkApiTestCase


class CookieFieldHandlerTestCaseSuccess(NetworkApiTestCase):
    """Class for testing the Cookie Field Handler."""

    def test_get_cookie_returns_ok_1(self):
        """Test get_cookie for ACL id 150000."""

        assert_equal(CookieHandler.get_cookie(150000),
                     644245094400000)

    def test_get_cookie_returns_ok_2(self):
        """Test get_cookie for ACL id 85434."""

        assert_equal(CookieHandler.get_cookie(85434),
                     366936235966464)

    def test_get_cookie_returns_ok_3(self):
        """Test get_cookie for ACL id 76535."""

        assert_equal(CookieHandler.get_cookie(76535),
                     328715321999360)

    def test_get_cookie_returns_ok_4(self):
        """Test get_cookie for ACL id 25194623."""

        assert_equal(CookieHandler.get_cookie(25194623),
                     108210081820049408)

    def test_get_id_acl_returns_ok_1(self):
        """Test get_id_acl for cookie 644245631270912."""

        cookie = 644245094400000
        assert_equal(CookieHandler.get_id_acl(cookie),
                     150000)

    def test_get_id_acl_returns_ok_2(self):
        """Test get_id_acl for cookie 366936504401920."""

        cookie = 366936235966464
        assert_equal(CookieHandler.get_id_acl(cookie),
                     85434)

    def test_get_id_acl_returns_ok_3(self):
        """Test get_id_acl for cookie 328719348531200."""

        cookie = 328715321999360
        assert_equal(CookieHandler.get_id_acl(cookie),
                     76535)

    def test_get_id_acl_returns_ok_4(self):
        """Test get_id_acl for cookie 108210084772839424."""

        cookie = 108210081820049408
        assert_equal(CookieHandler.get_id_acl(cookie),
                     25194623)

