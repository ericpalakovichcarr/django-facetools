import datetime

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from facetools.test import FacebookTestCase
from facetools.test.testcases import get_app_name_from_test_case
from facetools.models import TestUser
from facetools.signals import sync_facebook_test_user
from facetools.integrations import fandjango

from fandjango.models import User

class GetAppNameTestCase(TestCase):

    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS

    def tearDown(self):
        settings.INSTALLED_APPS = self.old_installed_apps

    def test_get_app_name_from_test_case(self):
        f = get_app_name_from_test_case
        settings.INSTALLED_APPS = settings.INSTALLED_APPS + ("the_app",)
        self.assertEquals("the_app", f("the_app.tests"))
        self.assertEquals("the_app", f("the_app.tests.test_module"))
        self.assertEquals("the_app", f("apps.the_app.tests.test_module"))
        self.assertRaises(ValueError, f, "tests.tests")
        self.assertRaises(ValueError, f, "tests.tests.test_module")
        self.assertRaises(ValueError, f, "the_app.tests_module")
        self.assertRaises(ValueError, f, "the_not_installed_app.tests")
        self.assertRaises(ValueError, f, "the_not_installed_app.tests.test_module")
        self.assertRaises(ValueError, f, "apps.the_not_installed_app.tests.test_module")

class TestFacebookTestCaseFixture1(FacebookTestCase):

    def test_user_fixture_loaded(self):
        self.client.facebook_login("Unittest Mako")
        self.assertEquals(2, TestUser.objects.count())
        self.assertTrue(TestUser.objects.filter(name="Unittest Shinra").exists())
        self.assertEquals(self.client.test_user, TestUser.objects.get(name="Unittest Mako"))
        self.assertEquals("Unittest Mako", self.client.test_user.name)

class TestFacebookTestCaseFixture2(FacebookTestCase):
    fixtures = ['junk_fixture.json']

    def test_user_fixture_loaded(self):
        self.client.facebook_login("Unittest Mako")
        self.assertEquals(3, TestUser.objects.count())
        self.assertTrue(TestUser.objects.filter(name="Unittest Shinra").exists())
        self.assertTrue(TestUser.objects.filter(name="Unittest Junk").exists())
        self.assertEquals(self.client.test_user, TestUser.objects.get(name="Unittest Mako"))
        self.assertEquals("Unittest Mako", self.client.test_user.name)

class TestFacebookTestCaseFixture3(FacebookTestCase):
    fixtures = ['junk_fixture.json', 'facetools_test_users_facetools_tests.json']

    def test_user_fixture_loaded(self):
        self.client.facebook_login("Unittest Mako")
        self.assertEquals(3, TestUser.objects.count())
        self.assertTrue(TestUser.objects.filter(name="Unittest Shinra").exists())
        self.assertTrue(TestUser.objects.filter(name="Unittest Junk").exists())
        self.assertEquals(self.client.test_user, TestUser.objects.get(name="Unittest Mako"))
        self.assertEquals("Unittest Mako", self.client.test_user.name)

class TestFacebookUsersSync(FacebookTestCase):
    fixtures = ['one_fandjango_user.json']

    def _pre_setup(self):
        sync_facebook_test_user.connect(fandjango.sync_facebook_test_user)
        super(TestFacebookUsersSync, self)._pre_setup()

    def _post_teardown(self):
        sync_facebook_test_user.disconnect(fandjango.sync_facebook_test_user)
        super(TestFacebookUsersSync, self)._post_teardown()

    def test_fixture_user_synced(self):
        user = User.objects.get(facebook_id=100003460044223)
        self.assertEquals("AAAESR2HSywMBAJu23BQ3f9RePbdG785Adhxw8Hkabotkq9oJE2CWGptph5ZBdSra35VyKJiayZAgK5aamCoOYZBLNPxXgC2i4fLi8qL29LYWz5Y9vZB6",
                          user.oauth_token.token)

class TestClient(FacebookTestCase):
    fixtures = ['one_fandjango_user.json']

    def _pre_setup(self):
        sync_facebook_test_user.connect(fandjango.sync_facebook_test_user)
        super(TestClient, self)._pre_setup()

    def _post_teardown(self):
        sync_facebook_test_user.disconnect(fandjango.sync_facebook_test_user)
        super(TestClient, self)._post_teardown()

    def test_fixture_user_signed_request(self):
        self.client.facebook_login("Unittest Mako")
        response = self.client.facebook_get(reverse("canvas:test_signed_request"))
        self.assertEquals(200, response.status_code)
        signed_request = response.context["signed_request"]

        # Check the signed request was correct
        self.assertEquals("100003460044223", signed_request['user_id'])
        self.assertEquals("AAAESR2HSywMBAJu23BQ3f9RePbdG785Adhxw8Hkabotkq9oJE2CWGptph5ZBdSra35VyKJiayZAgK5aamCoOYZBLNPxXgC2i4fLi8qL29LYWz5Y9vZB6",
                          signed_request['oauth_token'])

    def test_new_user_signed_request(self):
        self.client.facebook_login("Unittest Shinra")
        response = self.client.facebook_get(reverse("canvas:test_signed_request"))
        self.assertEquals(200, response.status_code)
        signed_request = response.context["signed_request"]

        # Check the signed request was correct
        self.assertEquals("100003536165092", signed_request['user_id'])
        self.assertEquals("AAAESR2HSywMBAEWJNr8m2xufpP2jIoHJ3aKTUREClHgDX3inIxCz4bCqAHZB8pA0cPnmBb7gD02eIdqcQirp7IDyHTlVlU95fWOiSGZBNbCzpU2fPz",
                          signed_request['oauth_token'])

    def test_first_then_second_user_requests(self):
        self.test_fixture_user_signed_request()
        self.test_new_user_signed_request()
