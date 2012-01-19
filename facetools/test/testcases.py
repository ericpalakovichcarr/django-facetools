from django.test.testcases import TestCase
from django.conf import settings
from facetools.models import TestUser
from facetools.common import _create_signed_request

# TODO: Add class that subclasses TransactionTestCase as well

class FacebookTestCase(TestCase):
    """
    TestCase which makes it possible to test views when the FacebookMiddleware
    and SyncFacebookUser middlewares are activated.  Must use the Client
    attached to this object (i.e. self.client).
    """
    facebook_test_user = None
    facebook_stop_sync_middleware = True

    def _pre_setup(self):
        if self.facebook_test_user:
            if not hasattr(self, 'fixtures'):
                self.fixtures = []
            if 'facetools_test_users.json' not in self.fixtures:
                self.fixtures.append('facetools_test_users.json')
            super(FacebookTestCase, self)._pre_setup()

            facebook_user = TestUser.objects.get(name=self.facebook_test_user)

            # TODO: Make this customizable
            from fandjango.models import User
            try:
                name_parts = facebook_user.name.split(" ")
                first_name = name_parts[0]
                last_name = name_parts[-1]
                middle_name = None
                if len(name_parts) < 2:
                    middle_name = " ".join(name_parts[1:-1])
                db_user = User.objects.get(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name)
                db_user.facebook_id = int(facebook_user.facebook_id)
                db_user.oauth_token.token = facebook_user.access_token
                db_user.save()
            except User.DoesNotExist:
                pass

            # Setup a signed request for the test client, so that any requests
            # made with the client will behave like the test user activated it
            # from facebook
            self.client.cookies['signed_request'] = _create_signed_request(
                settings.FACEBOOK_APPLICATION_SECRET_KEY,
                facebook_user.facebook_id,
                oauth_token=facebook_user.access_token
            )
        else:
            super(FacebookTestCase, self)._pre_setup()
