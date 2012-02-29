import types

from django.test.testcases import TestCase
from django.conf import settings
from facetools.models import TestUser
from facetools.common import _create_signed_request
from facetools.test import TestUserNotLoaded
from facetools.signals import sync_facebook_test_user, setup_facebook_test_client
from facetools.common import _get_facetools_test_fixture_name

# TODO: Add class that subclasses TransactionTestCase as well

class FacebookTestCase(TestCase):
    """
    TestCase which makes it possible to test views when the FacebookMiddleware
    and SyncFacebookUser middlewares are activated.  Must use the Client
    attached to this object (i.e. self.client).
    """
    facebook_test_user = None

    def _pre_setup(self):
        if self.facebook_test_user:
            if type(self.facebook_test_user) not in [str, unicode]:
                raise Exception("facebook_test_user variable must be a string (found a %s)" % type(self.facebook_test_user))

            app_name = get_app_name_from_test_case(type(self).__module__)
            facetools_fixture_name = _get_facetools_test_fixture_name(app_name)

            if not hasattr(self, 'fixtures'):
                self.fixtures = []
            if facetools_fixture_name not in self.fixtures:
                self.fixtures.append(facetools_fixture_name)
            super(FacebookTestCase, self)._pre_setup()

            # Make sure anybody that needs to sync their models loaded from fixtures
            # has a chance to do so now that the refreshed user test data is available.
            try:
                for test_user in TestUser.objects.all():
                    sync_facebook_test_user.send(sender=None, test_user=test_user)

                # Allow code to configure the test client so it has a signed request
                # of the specified test user for each request
                self.test_user = TestUser.objects.get(name=self.facebook_test_user)
                setup_facebook_test_client.send(sender=None, client=self.client, signed_request=_create_signed_request(
                    settings.FACEBOOK_APPLICATION_SECRET_KEY,
                    self.test_user.facebook_id,
                    oauth_token=self.test_user.access_token,
                ))
            except TestUser.DoesNotExist:
                raise TestUserNotLoaded("Test user %s hasn't been loaded via the %s fixture (did you run sync_facebook_test_users?)" %
                                        (self.facebook_test_user, facetools_fixture_name))
        else:
            super(FacebookTestCase, self)._pre_setup()

def get_app_name_from_test_case(module_path_string):
    """
    Gets thet Django app from the __class__ attribute of a TestCase in a Django app.
    class_string should look something like this: 'facetools_tests.tests.test_test_module'
    """
    packages = module_path_string.split(".")
    try:
        tests_location = packages.index("tests")
    except ValueError:
        raise ValueError("Couldn't find tests module in %s (are you running this test from tests.py or a tests package in your Django app?)" % module_path_string)
    if tests_location == 0:
        raise ValueError("Facetools doesn't support Django app's with a name of 'tests', or it failed to find the Django app name out of %s" % module_path_string)
    app_name = packages[tests_location - 1]
    if app_name not in settings.INSTALLED_APPS:
        raise ValueError("Facetools didn't find %s among INSTALLED_APPS. (app name pulled from %s)" % (app_name, module_path_string))
    return app_name
