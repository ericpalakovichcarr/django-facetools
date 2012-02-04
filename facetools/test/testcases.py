from django.test.testcases import TestCase
from django.conf import settings
from facetools.models import TestUser
from facetools.common import _create_signed_request
from facetools.test import TestUserNotLoaded
from facetools.signals import sync_facebook_test_user, setup_facebook_test_client
import types

# TODO: Add class that subclasses TransactionTestCase as well

class FacebookTestCase(TestCase):
    """
    TestCase which makes it possible to test views when the FacebookMiddleware
    and SyncFacebookUser middlewares are activated.  Must use the Client
    attached to this object (i.e. self.client).
    """
    facebook_test_user = None
    facetools_fixture_name = 'facetools_test_users.json'

    def _pre_setup(self):
        if self.facebook_test_user:
            if type(self.facebook_test_user) not in [str, unicode]:
                raise Exception("facebook_test_user variable must be a string (found a %s)" % type(self.facebook_test_user))

            if not hasattr(self, 'fixtures'):
                self.fixtures = []
            if self.facetools_fixture_name not in self.fixtures:
                self.fixtures.append(self.facetools_fixture_name)
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
                    oauth_token=self.test_user.access_token
                ))
            except TestUser.DoesNotExist:
                raise TestUserNotLoaded("Test user %s hasn't been loaded via the %s fixture (did you run sync_facebook_test_users?)" %
                                        (self.facebook_test_user, self.facetools_fixture_name))
        else:
            super(FacebookTestCase, self)._pre_setup()
