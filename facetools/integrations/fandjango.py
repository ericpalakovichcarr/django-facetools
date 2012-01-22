def sync_facebook_test_user(sender, **kwargs):
    from django.utils import importlib
    models = importlib.import_module('fandjango.models')
    try:
        name_parts = kwargs['test_user'].name.split(" ")
        first_name = name_parts[0]
        last_name = name_parts[-1]
        middle_name = None
        if len(name_parts) < 2:
            middle_name = " ".join(name_parts[1:-1])
        db_user = models.User.objects.get(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name)
        db_user.facebook_id = int(kwargs['test_user'].facebook_id)
        db_user.oauth_token.token = kwargs['test_user'].access_token
        db_user.save()
        db_user.oauth_token.save()
    except models.User.DoesNotExist:
        pass

def setup_facebook_test_client(sender, **kwargs):
    kwargs['client'].cookies['signed_request'] = kwargs['signed_request']
