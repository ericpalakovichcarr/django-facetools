from django.conf import settings
from fandjango.models import User
from fandjango.test.common import _create_test_user_on_facebook
from fandjango.utils import get_app_access_token, create_signed_request

def make_test_user(func):
    """
    Creates a test user for a test and deletes them when it finishes
    """
    def wrapper():
        try:
            facebook_data = _create_test_user_on_facebook(
                app_installed=True,
                name="Please Delete Me",
                access_token=get_app_access_token()
            )
            signed_request = create_signed_request(
                app_secret=settings.FACEBOOK_APPLICATION_SECRET_KEY,
                user_id=facebook_data['id'],
                issued_at=facebook_data['issued_at'],
                oauth_token=facebook_data['access_token']
            )
            func(signed_request)
        finally:
            for u in User.objects.filter(is_test_user==True):
                u.delete()
    return wrapper
make_test_user.__test__ = False
