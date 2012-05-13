import urllib
import datetime

from facetools import json
from facetools import settings
from facetools.common import _get_app_access_token, _create_permissions_string
from facetools.models import TestUser
import requests

class CreateTestUserError(Exception): pass
class CreateTestUserWarn(Warning): pass
class DeleteTestUserError(Exception): pass
class NotATestUser(Exception): pass

# -------------------------------------------------------------------------------------
# Functions for creating test users on facebook and in facetools
# -------------------------------------------------------------------------------------

def _create_test_user(app_installed=True, name=None, permissions=None, access_token=None):
    """
    Creates a test user on facebook and a corresponding User and OAuthToken object in the database.
    Friends can be set with set_test_user_friends after all test users are created.  Assumes
    test user with name doesn't already exist.
    """
    facebook_response_data = _create_test_user_on_facebook(
        app_installed=app_installed,
        name=name,
        permissions=permissions,
        access_token=access_token
    )
    _create_test_user_in_facetools(name, facebook_response_data)

def _create_test_user_on_facebook(app_installed=True, name=None, permissions=None, access_token=None):
    """
    Creates a test user on facebook.  Returns a dict of the json response from facebook.
    """
    test_user_template = "https://graph.facebook.com/%s/accounts/test-users?installed=%s&permissions=%s&method=post&access_token=%s"
    extended_token_template = "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=fb_exchange_token&fb_exchange_token=%s"

    # Generate the request URL
    if app_installed == True:
        app_installed = "true"
    else:
        app_installed = "false"
    if permissions is None:
        permissions = settings.FACEBOOK_APPLICATION_INITIAL_PERMISSIONS
    permissions = _create_permissions_string(permissions)
    if access_token is None:
        access_token = _get_app_access_token()
    test_user_url = test_user_template % (settings.FACEBOOK_APPLICATION_ID, app_installed, permissions, access_token)
    if name:
        test_user_url = '%s&name=%s' % (test_user_url,urllib.quote(name))

    # Request a new test user from facebook, giving it a few tries in case the endpoint has a temporary hiccup
    for attempts in range(settings.FACETOOLS_NUM_REQUEST_ATTEMPTS, 0, -1):
        r = requests.get(test_user_url, timeout=settings.FACETOOLS_REQUEST_TIMEOUT)
        try: data = json.loads(r.content)
        except: data = None
        if r.status_code != 200 or data is None or data == False or 'error' in data:
            if attempts > 0:
                continue
            try:
                raise CreateTestUserError(data['error']['message'])
            except:
                try:
                    raise CreateTestUserError("Request to create test user failed (status_code=%s and content=\"%s\")" % (r.status_code, r.content))
                except:
                    raise CreateTestUserError("Request to create test user failed (status_code=%s)" % r.status_code)
        break
    else:
        raise CreateTestUserError("Request to create test user failed")

    # Get an extended expiration date access token
    if data and data.get('access_token') is not None:
        extended_token_url = extended_token_template % (settings.FACEBOOK_APPLICATION_ID,
                                                        settings.FACEBOOK_APPLICATION_SECRET_KEY,
                                                        data['access_token'])
        data['access_token'] = _get_extended_token_json(extended_token_url)

    return data

def _get_create_user_json(test_user_url):
    """
    Sends a request to the Graph API for a new test user.  Returns the resulting JSON.
    """
    for attempts in range(settings.FACETOOLS_NUM_REQUEST_ATTEMPTS, 0, -1):
        r = requests.get(test_user_url, timeout=settings.FACETOOLS_REQUEST_TIMEOUT)
        try: data = json.loads(r.content)
        except: data = None
        if r.status_code != 200 or data is None or data == False or 'error' in data:
            if attempts > 0:
                continue
            try:
                raise CreateTestUserError(data['error']['message'])
            except:
                try:
                    raise CreateTestUserError("Request to create test user failed (status_code=%s and content=\"%s\")" % (r.status_code, r.content))
                except:
                    raise CreateTestUserError("Request to create test user failed (status_code=%s)" % r.status_code)
        break
    else:
        raise CreateTestUserError("Request to create test user failed")

    return data

def _get_extended_token_json(extended_token_url):
    """
    Sends a request to the Graph API for a new test user.  Returns the resulting JSON.
    """
    for attempts in range(settings.FACETOOLS_NUM_REQUEST_ATTEMPTS, 0, -1):
        r = requests.get(extended_token_url, timeout=settings.FACETOOLS_REQUEST_TIMEOUT)
        try: access_token = json.loads(r.content)
        except: access_token = None
        if r.status_code != 200 or access_token is None or access_token == False or 'error' in access_token:
            if attempts > 0:
                continue
            try:
                raise CreateTestUserWarn("Failed to extend access token: %s" % access_token['error']['message'])
            except:
                try:
                    raise CreateTestUserWarn("Request to extend access token failed (status_code=%s and content=\"%s\")" % (r.status_code, r.content))
                except:
                    raise CreateTestUserWarn("Request to extend access token failed (status_code=%s)" % r.status_code)
        break
    else:
        raise CreateTestUserWarn("Request to extend access token failed")

    return access_token

def _create_test_user_in_facetools(name, facebook_data):
    """
    Takes the JSON from creating a test user in the Graph API and creates a new TestUser record in the database.
    """
    # Add the user to the test user table
    if 'id' in facebook_data:
        from ipdb import set_trace; set_trace()
        expires = int(facebook_data.get('expires', 0))
        if not expires:
            expires = None
        else:
            expires = datetime.datetime.fromtimestamp(expires)
        try:
            test_user = TestUser.objects.get(facebook_id=int(facebook_data['id']))
        except TestUser.DoesNotExist:
            test_user = None
        if test_user is None:
            assert facebook_data['id'] is not None # This should never happen, so please freak out when it does
            TestUser.objects.create(
                name=name,
                facebook_id=str(facebook_data['id']),
                access_token=facebook_data.get('access_token'),
                access_token_expires=expires,
                login_url=facebook_data.get('login_url')
            )
        else:
            test_user.access_token = facebook_data.get('access_token')
            test_user.access_token_expires = expires
            test_user.login_url = facebook_data.get('login_url')
            test_user.save()
    else:
        raise Exception("Invalid facebook user data")

def _delete_test_user_on_facebook(test_user):
    delete_url_template = "https://graph.facebook.com/%s?method=delete&access_token=%s"
    delete_user_url = delete_url_template % (test_user.facebook_id, _get_app_access_token())
    r = requests.delete(delete_user_url)
    if not isinstance(r.content, basestring):
        raise DeleteTestUserError("Error deleting user %s (%s) from facebook: Facebook returned invalid response" % (test_user.name, test_user.facebook_id, r.content))
    if r.content.strip().lower() != "true":
        if r.content.strip().lower() == "false":
            raise DeleteTestUserError("Error deleting user %s (%s) from facebook: Facebook returned false" % (test_user.name, test_user.facebook_id, r.content))
        else:
            try:
                raise DeleteTestUserError("Error deleting user %s (%s) from facebook: %s" % (test_user.name, test_user.facebook_id, json.loads(r.content)['error']['message']))
            except:
                raise DeleteTestUserError("Error deleting user %s (%s) from facebook: %s" % (test_user.name, test_user.facebook_id, r.content))

# -------------------------------------------------------------------------------------
# Functions for creating friends between test users
# -------------------------------------------------------------------------------------

def _friend_test_users(user, friend):
    """
    Makes two users friends. user friend a list of other test users.  The list
    of friends can be a list containing either a string of the friends
    full name, or the User object to friend.
    """
    user = TestUser.objects.get(name=user)
    friend = TestUser.objects.get(name=friend)
    response = requests.get("https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" %
            (user.facebook_id, friend.facebook_id, user.access_token))
    __handle_friend_test_users_error(user, friend, response)
    response = requests.get("https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" %
            (friend.facebook_id, user.facebook_id, friend.access_token))
    __handle_friend_test_users_error(user, friend, response)

def __handle_friend_test_users_error(user, friend, response):
    error_message = "Failed to friend %s with %s" % (user.name, friend.name)
    try: rdata = json.loads(response.content)
    except: rdata = False

    if rdata == False:
        raise CreateTestUserError(error_message)
    elif type(rdata) is not bool and 'error' in rdata:
        if not __already_friends(rdata):
            try:
                error_message += " (%s)" % rdata['error']['message']
            finally:
                raise CreateTestUserError(error_message)
    elif response.status_code != 200:
        raise CreateTestUserError(error_message)

def __already_friends(response_data):
    are_already_friends = False
    if 'error' in response_data and 'message' in response_data['error']:
        if 'You are already friends with this user' in response_data['error']['message']:
            are_already_friends = True
    return are_already_friends
