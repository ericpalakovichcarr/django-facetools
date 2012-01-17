import urllib
import json
import datetime

from django.conf import settings
from fandjango.models import User, OAuthToken
from fandjango.utils import create_user_from_token
from facetools.common import _get_app_access_token, _create_permissions_string
import requests

class CreateTestUserError(Exception): pass
class NotATestUser(Exception): pass

# -------------------------------------------------------------------------------------
# Functions that should be used by users of Fandjango
# -------------------------------------------------------------------------------------

def create_test_user(app_installed=True, name=None, permissions=None, access_token=None):
    """
    Creates a test user on facebook and a corresponding User and OAuthToken object in the database.
    Friends can be set with set_test_user_friends after all test users are created.
    """
    facebook_response_data = _create_test_user_on_facebook(
        app_installed=app_installed,
        name=name,
        permissions=permissions,
        access_token=access_token
    )
    return _create_test_user_in_fandjango(facebook_response_data)

def friend_test_users(user, friend):
    """
    Makes two users friends. user friend a list of other test users.  The list
    of friends can be a list containing either a string of the friends
    full name, or the User object to friend.
    """
    user = _name_to_test_user(user)
    friend = _name_to_test_user(friend)
    response = requests.get("https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" %
            (user.facebook_id, friend.facebook_id, user.oauth_token.token))
    _handle_friend_test_users_error(user, friend, response)
    response = requests.get("https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s" %
            (friend.facebook_id, user.facebook_id, friend.oauth_token.token))
    _handle_friend_test_users_error(user, friend, response)

def _already_friends(response_data):
    are_already_friends = False
    if 'error' in response_data and 'message' in response_data['error']:
        if 'You are already friends with this user' in response_data['error']['message']:
            are_already_friends = True
    return are_already_friends

def _handle_friend_test_users_error(user, friend, response):
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

# -------------------------------------------------------------------------------------
# Functions that shouldn't be used by users of Fandjango except for special cases
# -------------------------------------------------------------------------------------

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
    permissions = _create_permissions_string(permissions)
    if access_token is None:
        access_token = _get_app_access_token()
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

def _create_test_user_in_fandjango(facebook_data):
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

def _name_to_test_user(test_user_name):
    """
    Takes a test user's full name and returns their User object.
    """
    # Do nothing if a User was passed in,
    if type(test_user_name) is not User:
        try:
            parts = [str(p) for p in test_user_name.split(' ')]
            assert len(parts) > 0
        except:
            raise Exception("Invalid user name (%s)" % test_user_name)
        first_name = parts[0]
        last_name = parts[-1] # note: facebook takes single name users and sets their first and last names to the one name, so this is okay if there's only one element in the parts array
        middle_name = None
        if len(parts) > 2:
            middle_name = " ".join(parts[1:-1])
        return User.objects.get(is_test_user=True, first_name=first_name, middle_name=middle_name, last_name=last_name)
    return test_user_name

def _get_relationships(test_users):
    """
    Takes a facebook_test_users dict and returns a list of relationships, with
    each item being a set of 2 names that should be friends.
    """
    relationships = []
    for test_user in test_users:
        if 'friends' in test_user:
            for friend in test_user['friends']:
                relationships.append(set([test_user['name'], friend]))
    no_dupes = []
    for relationship in relationships:
        if relationship not in no_dupes:
            no_dupes.append(relationship)
    return no_dupes
