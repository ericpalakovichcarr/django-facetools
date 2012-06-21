import datetime

def sync_facebook_test_user(sender, **kwargs):
    from django.utils import importlib
    models = importlib.import_module('fandjango.models')

    # Split out the test user's name
    name_parts = kwargs['test_user'].name.split(" ")
    first_name = name_parts[0]
    last_name = name_parts[-1]
    middle_name = None
    if len(name_parts) < 2:
        middle_name = " ".join(name_parts[1:-1])

    # Update the Fandjango user with the same name, creating a new one if need be
    # Either don't create a new one or delete the user if the app isn't installed for the test user.
    user_installed_app = kwargs['test_user'].access_token is not None and len(kwargs['test_user'].access_token) > 0
    try:
        db_user = models.User.objects.get(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name)
        db_user.facebook_id = int(kwargs['test_user'].facebook_id)
        db_user.authorized = user_installed_app
        oauth_token = models.OAuthToken()
        if user_installed_app:
            oauth_token.token = kwargs['test_user'].access_token
            oauth_token.issued_at = datetime.datetime.now()
            oauth_token.expires_at = kwargs['test_user'].access_token_expires
        else:
            oauth_token.token = ""
            oauth_token.issued_at = datetime.datetime.fromtimestamp(0)
            oauth_token.expires_at = datetime.datetime.fromtimestamp(0)
        oauth_token.save()
        db_user.oauth_token = oauth_token
        db_user.save()

    except models.User.DoesNotExist:
        pass
