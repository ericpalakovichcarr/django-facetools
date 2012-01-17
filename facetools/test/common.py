import urllib
import json
import datetime

from django.conf import settings
from facetools.common import get_app_access_token, create_permissions_string
from facetools.models import TestUser
import requests

class CreateTestUserError(Exception): pass
class NotATestUser(Exception): pass

# -------------------------------------------------------------------------------------
# Functions for creating test users on facebook and in facetools
# -------------------------------------------------------------------------------------

def create_test_user(app_installed=True, name=None, permissions=None, access_token=None):
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

    # Generate the request URL
    if app_installed == True:
        app_installed = "true"
    else:
        app_installed = "false"
    if permissions is None:
        permissions = settings.FACEBOOK_APPLICATION_INITIAL_PERMISSIONS
    permissions = create_permissions_string(permissions)
    if access_token is None:
        access_token = get_app_access_token()
    test_user_url = test_user_template % (settings.FACEBOOK_APPLICATION_ID, app_installed, permissions, access_token)
    if name:
        test_user_url = '%s&name=%s' % (test_user_url,urllib.quote(name))

    # Request a new test user from facebook
    r = requests.get(test_user_url)
    if r.status_code == 200:
        data = json.loads(r.content)
        if 'error' in data:
            try:
                raise CreateTestUserError(data['error']['message'])
            except:
                raise CreateTestUserError("Request to create test user failed (call to facebook api failed)")
        elif data == 'false':
            raise CreateTestUserError("Request to create test user failed (call to facebook api returned false)")

        # Successfull call
        else:
            return data
    else:
        try:
            data = json.loads(r.content)
            raise CreateTestUserError(data['error']['message'])
        except:
            raise CreateTestUserError("Request to create test user failed (status code %s)" % r.status_code)

def _create_test_user_in_facetools(name, facebook_data):
    # Add the user to the test user table
    if 'id' in facebook_data:
        try:
            test_user = TestUser.objects.get(facebook_id=int(facebook_data['id']))
        except TestUser.DoesNotExist:
            test_user = None
        if test_user is None:
            test_user = TestUser.objects.create(
                name=name,
                facebook_id=str(facebook_data['id']),
                access_token=str(facebook_data.get('access_token', ""))
            )
        else:
            test_user.access_token = str(facebook_data.get('access_token', ""))
            test_user.save()
    else:
        raise Exception("Invalid facebook user data")

# -------------------------------------------------------------------------------------
# Functions for creating friends between test users
# -------------------------------------------------------------------------------------

def friend_test_users(user, friend):
    """
    Makes two users friends. user friend a list of other test users.  The list
    of friends can be a list containing either a string of the friends
    full name, or the User object to friend.
    """
    user = TestUser.objects.get(name=user)
    friend = TestUser.objects.get(name=friend)
    response = requests.get("https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" %
            (user.facebook_id, friend.facebook_id, user.oauth_token.token))
    _handle_friend_test_users_error(user, friend, response)
    response = requests.get("https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" %
            (friend.facebook_id, user.facebook_id, friend.oauth_token.token))
    _handle_friend_test_users_error(user, friend, response)

def __handle_friend_test_users_error(user, friend, response):
    error_message = "Failed to friend %s with %s" % (user.full_name, friend.full_name)
    try: rdata = json.loads(response.content)
    except: rdata = False

    if rdata == False:
        raise CreateTestUserError(error_message)
    elif type(rdata) is not bool and 'error' in rdata:
        if not _already_friends(rdata):
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