from facetools.tests.decorators import make_test_user

@make_test_user
def test_facebook_post_method_override(signed_request):
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware

    request = RequestFactory().post('/', {'signed_request': signed_request})
    FacebookMiddleware().process_request(request)

    assert request.method == 'GET'

@make_test_user
def test_fandjango_registers_user(signed_request):
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import User

    request = RequestFactory().post('/', {'signed_request': signed_request})
    FacebookMiddleware().process_request(request)

    user = User.objects.get(id=1)

    assert user.first_name == 'Please'
    assert user.last_name == 'Delete'
    assert user.full_name == 'Me'
    assert user.gender == 'male' or user.gender == 'female'
    assert user.profile_url in [
        'http://www.facebook.com/profile.php?id=%s' % signed_request['user_id'],
        'https://www.facebook.com/profile.php?id=%s' % signed_request['user_id'],
    ]

@make_test_user
def test_fandjango_registers_oauth_token(signed_request):
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import OAuthToken
    import datetime

    request = RequestFactory().post('/', {'signed_request': signed_request})
    FacebookMiddleware().process_request(request)

    token = OAuthToken.objects.get(id=1)

    assert token.token == signed_request['oauth_token']
    assert token.issued_at == datetime.datetime.fromtimestamp(signed_request['issued_at'])
    assert token.expires_at == None