from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import management
from facetools.test import FacebookTestCase
from facetools.models import TestUser
from fandjango.models import User

class FacebookTestCaseTests(TestCase):
    fixtures = ['facebook_users.json']

    def test_sync_management_command_integration(self):
        self.assertEquals(2, User.objects.count())
        self.assertEquals(0, TestUser.objects.count())
        old_data = {}
        for user in User.objects.all():
            old_data[user.id] = {
                'facebook_id': user.facebook_id,
                'access_token': user.oauth_token.token
            }

        management.call_command('sync_facebook_test_users', 'canvas')
        self.assertEquals(2, User.objects.count())
        self.assertEquals(3, TestUser.objects.count())
        for user in User.objects.all():
            self.assertNotEquals(old_data[user.id]['facebook_id'], user.facebook_id)
            self.assertNotEquals(old_data[user.id]['access_token'], user.facebook_id)
            test_user = TestUser.objects.get(facebook_id=user.facebook_id)
            self.assertEquals(test_user.access_token, user.oauth_token.token)

class FandjangoViewIntegrationTests(FacebookTestCase):
    fixtures = ['facebook_users.json']
    facebook_test_user = 'Unittest Samsonite'

    def test_facebooktestcase_integration(self):
        self.assertEquals(2, User.objects.count())
        self.assertEquals(3, TestUser.objects.count())
        for user in User.objects.all():
            test_user = TestUser.objects.get(facebook_id=user.facebook_id)
            self.assertEquals(test_user.access_token, user.oauth_token.token)

    def test_signed_request_integration(self):
        response = self.client.get(reverse("canvas:test_url"))
        self.assertEquals(200, response.status_code)
        facebook = response.context['facebook']
        self.assertIn(str(facebook.user.facebook_id), response.content)
        self.assertIn(str(facebook.user.oauth_token.token), response.content)
        self.assertEquals("en_US", facebook.user.locale) # should result in facebook api call in fandjango
