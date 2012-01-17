from optparse import make_option
import json

from django.core.management.base import AppCommand, BaseCommand
from django.conf import settings
import requests

from fandjango.test import create_test_user, friend_test_users
from fandjango.test.common import _get_relationships

class Command(AppCommand):
    help = 'Creates the facebook test users defined in each app in the project.'
    option_list = BaseCommand.option_list + (
        make_option('--allow_duplicate_users', action="store_true", dest='allow_duplicate_users',
            help='Specifies the indent level to use when pretty-printing output'),
    )

    def handle_app(self, app, **options):
        allow_duplicate_users = options.get('allow_duplicate_users', False)
        app_name = '.'.join(app.__name__.split('.')[0:-1])

        fandjango_test_users = get_fandjango_test_users(app_name)
        if not allow_duplicate_users:
            existing_facebook_test_users = get_existing_facebook_test_users()

        # Create any test users on facebook their corresponding User models in fandjango
        # that don't exist on facebook yet
        for fandjango_test_user in fandjango_test_users:
            if allow_duplicate_users or fandjango_test_user['name'] not in existing_facebook_test_users:
                fandjango_test_user['user'] = create_test_user(
                    app_installed=fandjango_test_user.get('installed'),
                    name=fandjango_test_user.get('name'),
                    permissions=fandjango_test_user.get('permissions'),
                )

        # Get a list of each relationship between test users, no duplicates
        relationships = [list(r) for r in _get_relationships(fandjango_test_users)]
        for relationship in relationships:
            relationship = list(relationship)
            friend_test_users(relationship[0], relationship[1])

def get_fandjango_test_users(app_name, test_user_module_name='facebook_test_users'):
    """Get the dictionary of facebook test users for the app, throwing an error if the app
    doesn't have any defined."""

    try:
        _temp = __import__(app_name, globals(), locals(), [test_user_module_name])
        fandjango_test_users = _temp.facebook_test_users.facebook_test_users
        if callable(fandjango_test_users):
            fandjango_test_users = fandjango_test_users()
    except ImportError:
        raise Exception("Error: %s doesn't have a module called %s" % (app_name, test_user_module_name))

    # Ensure no test users share the same name
    fandjango_test_names = set([u['name'] for u in fandjango_test_users])
    if len(fandjango_test_names) != len(fandjango_test_users):
        raise Exception("Error: Duplicate names found in %s for %s" % (test_user_module_name, app_name))

    return fandjango_test_users

def get_existing_facebook_test_users(app_id=settings.FACEBOOK_APPLICATION_ID, app_secret=settings.FACEBOOK_APPLICATION_SECRET_KEY):
    existing_facebook_test_users = {}
    app_access_token = '%s|%s' % (app_id, app_secret)
    test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (app_id, app_access_token)
    users_response_data = json.loads(requests.get(test_users_url).content)
    if 'error' in users_response_data:
        raise Exception("Error retrieving facebook app's test users: %s" % users_response_data['error']['message'])
    else:
        test_user_url = "https://graph.facebook.com/%s?access_token=%s"
        for test_user in users_response_data['data']:
            user_response_data = json.loads(requests.get(test_user_url % (test_user['id'], app_access_token)).content)
            if user_response_data == False:
                # skip invalid users
                continue
            if 'error' in user_response_data:
                raise Exception("Error retrieving data for %s: %s" % (test_user['id'], user_response_data['error']['message']))
            elif 'name' in user_response_data:
                existing_facebook_test_users[user_response_data['name']] = user_response_data

    return existing_facebook_test_users
