from nose.tools import assert_equal

from networkapi.plugins.SDN.ODL.utils.cookie_handler import CookieHandler
from networkapi.test.test_case import NetworkApiTestCase


class CookieFieldHandlerTestCaseSuccess(NetworkApiTestCase):
    """Class for testing the Cookie Field Handler."""

    def test_get_cookie_returns_ok_1(self):
        """Test get_cookie for ACL id 150000."""

        assert_equal(CookieHandler(150000).cookie, 644245094400000)

    def test_get_cookie_returns_ok_2(self):
        """Test get_cookie for ACL id 85434."""

        assert_equal(CookieHandler(85434).cookie,
                     366936235966464)

    def test_get_cookie_returns_ok_3(self):
        """Test get_cookie for ACL id 76535."""

        assert_equal(CookieHandler(76535).cookie,
                     328715321999360)

    def test_get_cookie_returns_ok_4(self):
        """Test get_cookie for ACL id 25194623."""

        assert_equal(CookieHandler(25194623).cookie,
                     108210081820049408)

    def test_get_id_acl_returns_ok_1(self):
        """Test get_id_acl for cookie 644245631270912."""

        assert_equal(CookieHandler(150000).get_id_acl(),
                     150000)

    def test_get_id_acl_returns_ok_2(self):
        """Test get_id_acl for cookie 366936504401920."""

        assert_equal(CookieHandler(85434, id_env=42).get_id_acl(),
                     85434)

    def test_get_id_environment(self):
        """Test get_id_environment from cookie """

        assert_equal(CookieHandler(25194623, id_env=10).get_id_environment(),
                     10)

