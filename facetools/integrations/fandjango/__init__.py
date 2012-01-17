import datetime

from fandjango.models import User, OAuthToken

def __create_test_user_in_fandjango(facebook_data):
    """
    Creates a User and OAuthToken object for a facebook test user.  Expects a dict with the following:
    id - The facebook id of the user
    """
    if 'id' in facebook_data:
        token = facebook_data.get('access_token', "")
        oauth_token = OAuthToken.objects.create(
            token = token,
            issued_at = datetime.datetime.now(),
            expires_at = None if token else datetime.datetime.now()
        )
        try: user = User.objects.get(facebook_id=int(facebook_data['id']))
        except User.DoesNotExist: user = None
        if user is None:
            user = create_user_from_token(oauth_token)
            user.is_test_user = True
            user.save()
        else:
            user.is_test_user = True
            user.oauth_token = oauth_token
            user.save()

        return user
    else:
        raise Exception("Invalid facebook user data")