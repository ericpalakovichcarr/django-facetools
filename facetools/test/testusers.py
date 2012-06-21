import time
import datetime
import urllib
import urlparse

from facetools import json
from facetools import settings
from facetools.common import _get_app_access_token, _create_permissions_string, _get_facebook_graph_data
from facetools.models import TestUser
import requests

class CreateTestUserError(Exception): pass
class CreateTestUserWarn(Warning): pass
class DeleteTestUserError(Exception): pass

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
    _create_test_user_in_facetools(facebook_response_data)

def _create_test_user_on_facebook(app_installed=True, name=None, permissions=None, access_token=None):
    """
    Creates a test user on facebook.  Returns a dict of the json response from facebook, including their access token,
    id, and their user information (name, gender, other things the app has permissions for).
    """
    test_user_create_template = "https://graph.facebook.com/%s/accounts/test-users?installed=%s&permissions=%s&method=post&access_token=%s"
    extended_token_template = "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=fb_exchange_token&fb_exchange_token=%s"
    test_user_info_template = "https://graph.facebook.com/%s?access_token=%s"

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
    test_user_create_url = test_user_create_template % (settings.FACEBOOK_APPLICATION_ID, app_installed, permissions, access_token)
    if name:
        test_user_create_url = '%s&name=%s' % (test_user_create_url,urllib.quote(name))

    # Create the test user
    new_test_user_create_data = _get_facebook_graph_data(test_user_create_url, CreateTestUserError, "Request to create test user failed")
    new_test_user_create_data['access_token_extended'] = False

    # Get the new test user's open graph user data
    test_user_info_url = test_user_info_template % (new_test_user_create_data['id'], access_token)
    new_test_user_info_data = _get_facebook_graph_data(test_user_info_url, CreateTestUserError, "Request to pull new test user's info failed")

    # Get an extended access token for the test user
    if new_test_user_create_data.get('access_token') is not None:
        extended_token_url = extended_token_template % (settings.FACEBOOK_APPLICATION_ID,
                                                        settings.FACEBOOK_APPLICATION_SECRET_KEY,
                                                        new_test_user_create_data['access_token'])
        response_content = _get_facebook_graph_data(extended_token_url, CreateTestUserWarn,
                                                    "Request to extend access token failed", convert_to_json=False)
        parts = urlparse.parse_qs(response_content)
        new_test_user_create_data['access_token'] = parts["access_token"][0]
        new_test_user_create_data['access_token_expires'] = datetime.datetime.fromtimestamp(
                                                                time.mktime(datetime.datetime.now().timetuple()) +
                                                                int(parts["expires"][0]))

    # Join the data from the create call and the info call and return to caller
    return dict(new_test_user_create_data, **new_test_user_info_data)

def _delete_test_user_on_facebook(test_user):
    """
    Deletes a test user from facebook.
    """
    delete_url_template = "https://graph.facebook.com/%s?method=delete&access_token=%s"
    delete_user_url = delete_url_template % (test_user.facebook_id, _get_app_access_token())
    _get_facebook_graph_data(delete_user_url, DeleteTestUserError,
                             "Error deleting test user %s (%s) from facebook" % (test_user.name, test_user.facebook_id),
                             method="delete", convert_to_json=False, fail_test=lambda r: r.content.strip().lower() != "true")

def _create_test_user_in_facetools(facebook_data):
    """
    Takes the JSON from creating a test user in the Graph API and creates a new TestUser record in the database.
    """
    # Add the user to the test user table
    try:
        test_user = TestUser.objects.get(facebook_id=int(facebook_data['id']))
    except TestUser.DoesNotExist:
        test_user = TestUser()
    test_user._populate_from_graph_data(facebook_data)
    test_user.save()

def _friend_test_users(user, friend):
    """
    Makes two users friends. user friend a list of other test users.  The list
    of friends can be a list containing either a string of the friends
    full name, or the User object to friend.
    """
    user = TestUser.objects.get(name=user)
    friend = TestUser.objects.get(name=friend)
    friend_url_a_to_b = "https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" % (user.facebook_id, friend.facebook_id, user.access_token)
    friend_url_b_to_a = "https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" % (friend.facebook_id, user.facebook_id, friend.access_token)
    already_friends = lambda r: 'You are already friends with this user' in r.content

    _get_facebook_graph_data(friend_url_a_to_b, CreateTestUserError, "Failed to friend %s with %s" % (user.name, friend.name),
                             success_test=already_friends)
    _get_facebook_graph_data(friend_url_b_to_a, CreateTestUserError, "Failed to friend %s with %s" % (friend.name, user.name),
                             success_test=already_friends)
