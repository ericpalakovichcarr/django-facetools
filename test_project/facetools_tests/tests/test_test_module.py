import datetime

from django.test import TestCase
from django.conf import settings

from facetools.test import FacebookTestCase
from facetools.test.testcases import get_app_name_from_test_case
from facetools.signals import setup_facebook_test_client
from facetools.models import TestUser
from facetools.signals import setup_facebook_test_client, sync_facebook_test_user
from facetools.integrations import fandjango
from facetools.common import _parse_signed_request

from fandjango.models import User

setup_facebook_test_client.connect(fandjango.setup_facebook_test_client)

class GetAppNameTestCase(TestCase):

    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS

    def tearDown(self):
        settings.INSTALLED_APPS = self.old_installed_apps

    def test_get_app_name_from_test_case(self):
        f = get_app_name_from_test_case
        settings.INSTALLED_APPS = settings.INSTALLED_APPS + ["the_app",]
        self.assertEquals("the_app", f("the_app.tests"))
        self.assertEquals("the_app", f("the_app.tests.test_module"))
        self.assertEquals("the_app", f("apps.the_app.tests.test_module"))
        self.assertRaises(ValueError, f, "tests.tests")
        self.assertRaises(ValueError, f, "tests.tests.test_module")
        self.assertRaises(ValueError, f, "the_app.tests_module")
        self.assertRaises(ValueError, f, "the_not_installed_app.tests")
        self.assertRaises(ValueError, f, "the_not_installed_app.tests.test_module")
        self.assertRaises(ValueError, f, "apps.the_not_installed_app.tests.test_module")

class TestFacebookTestCase1(FacebookTestCase):

    def setUp(self):
        self.test_client.set_facebook_test_user("Unittest Mako")

    def test_user_fixture_loaded(self):
        self.assertEquals(2, TestUser.objects.count())
        self.assertEquals(1, TestUser.objects.filter(name="Unittest Shinra").count())
        self.assertEquals(self.test_user, TestUser.objects.get(name="Unittest Mako"))
        self.assertEquals("Unittest Mako", self.test_user.name)

class TestFacebookTestCase2(FacebookTestCase):
    fixtures = ['junk_fixture.json']

    def setUp(self):
        self.test_client.set_facebook_test_user("Unittest Mako")

    def test_user_fixture_loaded(self):
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(1, TestUser.objects.filter(name="Unittest Shinra").count())
        self.assertEquals(1, TestUser.objects.filter(name="Unittest Junk").count())
        self.assertEquals(self.test_user, TestUser.objects.get(name="Unittest Mako"))
        self.assertEquals("Unittest Mako", self.test_user.name)

class TestFacebookTestCase3(FacebookTestCase):
    fixtures = ['junk_fixture.json', 'facetools_test_users_facetools_tests.json']

    def setUp(self):
        self.test_client.set_facebook_test_user("Unittest Mako")

    def test_user_fixture_loaded(self):
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(1, TestUser.objects.filter(name="Unittest Shinra").count())
        self.assertEquals(1, TestUser.objects.filter(name="Unittest Junk").count())
        self.assertEquals(self.test_user, TestUser.objects.get(name="Unittest Mako"))
        self.assertEquals("Unittest Mako", self.test_user.name)

class TestFandjangoIntegration(FacebookTestCase):
    fixtures = ['one_fandjango_user.json']

    def setUp(self):
        self.test_client.set_facebook_test_user("Unittest Mako")

    def _pre_setup(self):
        setup_facebook_test_client.connect(fandjango.setup_facebook_test_client)
        sync_facebook_test_user.connect(fandjango.sync_facebook_test_user)
        super(TestFandjangoIntegration, self)._pre_setup()

    def _post_teardown(self):
        setup_facebook_test_client.disconnect(fandjango.setup_facebook_test_client)
        sync_facebook_test_user.disconnect(fandjango.sync_facebook_test_user)
        super(TestFandjangoIntegration, self)._post_teardown()

    def test_integration(self):
        self.assertEquals(2, User.objects.count())
        mako = User.objects.get(facebook_id="100003460044223")
        shinra = User.objects.get(facebook_id="100003536165092")
        self.assertEquals("Unittest Mako", mako.full_name)
        self.assertEquals("Unittest Shinra", shinra.full_name)
        self.assertEquals(datetime.date(1980,8,8), mako.birthday)
        self.assertEquals(None, shinra.birthday)
        self.assertEquals("AAAESR2HSywMBAJu23BQ3f9RePbdG785Adhxw8Hkabotkq9oJE2CWGptph5ZBdSra35VyKJiayZAgK5aamCoOYZBLNPxXgC2i4fLi8qL29LYWz5Y9vZB6",
                          mako.oauth_token.token)
        self.assertEquals("AAAESR2HSywMBAEWJNr8m2xufpP2jIoHJ3aKTUREClHgDX3inIxCz4bCqAHZB8pA0cPnmBb7gD02eIdqcQirp7IDyHTlVlU95fWOiSGZBNbCzpU2fPz",
                          shinra.oauth_token.token)
        signed_request = _parse_signed_request(self.client.cookies['signed_request'].value, settings.FACEBOOK_APPLICATION_SECRET_KEY)
        self.assertEquals("100003460044223", signed_request['user_id'])
        self.assertEquals("AAAESR2HSywMBAJu23BQ3f9RePbdG785Adhxw8Hkabotkq9oJE2CWGptph5ZBdSra35VyKJiayZAgK5aamCoOYZBLNPxXgC2i4fLi8qL29LYWz5Y9vZB6",
                          signed_request['oauth_token'])
