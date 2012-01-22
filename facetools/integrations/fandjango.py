def sync_facebook_test_user(sender, **kwargs):
    from fandjango.models import User
    try:
        name_parts = kwargs['test_user'].name.split(" ")
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

def setup_facebook_test_client(sender, **kwargs):
    kwargs['client'].cookies['signed_request'] = kwargs['signed_request']