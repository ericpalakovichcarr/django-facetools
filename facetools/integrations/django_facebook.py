def sync_facebook_test_user(sender, **kwargs):
    from django_facebook.models import FacebookProfileModel
    try:
        db_user = FacebookProfileModel.objects.get(facebook_name=kwargs['test_user'].name)
        db_user.facebook_id = int(facebook_user.facebook_id)
        db_user.access_token = facebook_user.access_token
        db_user.save()
    except FacebookProfileModel.DoesNotExist:
        pass

def setup_facebook_test_client(sender, **kwargs):
    from django.conf import settings
    cookie_name = 'fbsr_%s' % settings.FACEBOOK_APP_ID
    kwargs['client'].cookies[cookie_name] = kwargs['signed_request']
