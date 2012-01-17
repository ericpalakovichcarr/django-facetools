from django.test.testcases import TestCase
from django.conf import settings
from fandjango.models import User, OAuthToken
from fandjango.utils import create_signed_request

# TODO: Add class that subclasses TransactionTestCase as well

class FacebookTestCase(TestCase):
    """
    TestCase which makes it possible to test views when the FacebookMiddleware
    and SyncFacebookUser middlewares are activated.  Must use the Client
    attached to this object (i.e. self.client).
    """
    facebook_user = None
    facebook_stop_sync_middleware = True

    def _pre_setup(self):
        super(FacebookTestCase, self)._pre_setup()

        # Don't change anything if a faebook user wasn't specified
        if self.facebook_user:
            facebook_user = User.objects.get(facebook_id=self.facebook_user)

            # Add a signed_request to the request
            oauth_token = None
            if OAuthToken.objects.filter(pk=facebook_user.pk).count():
                oauth_token = OAuthToken.objects.get(pk=facebook_user.pk).token
            self.client.cookies['signed_request'] = create_signed_request(
                settings.FACEBOOK_APPLICATION_SECRET_KEY,
                facebook_user.facebook_id, oauth_token=oauth_token
            )
