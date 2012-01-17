import json
import copy

import requests
from django.test import TestCase
from django.core import management

from mock_django.settings import FACEBOOK_APPLICATION_ID, FACEBOOK_APPLICATION_SECRET_KEY
from fandjango.models import User

class CreateFacebookTestUsersTests(TestCase):

    def tearDown(self):
        for test_user in User.objects.filter(is_test_user=True):
            test_user.delete() # should also delete facebook test user through delete method override

    def test_creating_one_user(self):
        from mock_django.testapp1.facebook_test_users import facebook_test_users
        self.assertEquals(0, User.objects.count())
        app_access_token = '%s|%s' % (FACEBOOK_APPLICATION_ID, FACEBOOK_APPLICATION_SECRET_KEY)

        management.call_command('create_facebook_test_users', 'testapp1', allow_duplicate_users=True)

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (FACEBOOK_APPLICATION_ID, app_access_token)
        api_test_users = json.loads(requests.get(test_users_url).content)['data']
        test_users = merge_with_facebook_data(facebook_test_users, api_test_users, app_access_token)

        # Make sure the test user's information on facebook is correct
        self.assertEquals(1, len(test_users))
        self.assertEquals(1, len([u for u in test_users if u.get('graph_user_data') and u.get('graph_permission_data')]))
        for permission in test_users[0]['permissions']:
            self.assertTrue(permission.strip() in test_users[0]['graph_permission_data']['data'][0])

        # Make sure the test user's information in Fandjango is correct
        self.assertEquals(1, User.objects.count())
        user = User.objects.get()
        self.assertTrue(user.is_test_user)
        self.assertEquals(test_users[0]['graph_user_data']['id'], str(user.facebook_id))
        self.assertEquals(test_users[0]['name'], user.full_name)

    def test_overwrite_one_user(self):
        from mock_django.testapp1.facebook_test_users import facebook_test_users
        self.assertEquals(0, User.objects.count())
        app_access_token = '%s|%s' % (FACEBOOK_APPLICATION_ID, FACEBOOK_APPLICATION_SECRET_KEY)

        management.call_command('create_facebook_test_users', 'testapp1', allow_duplicate_users=True)
        management.call_command('create_facebook_test_users', 'testapp1')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (FACEBOOK_APPLICATION_ID, app_access_token)
        api_test_users = json.loads(requests.get(test_users_url).content)['data']
        test_users = merge_with_facebook_data(facebook_test_users, api_test_users, app_access_token)

        # Make sure the test user's information on facebook is correct
        self.assertEquals(1, len(test_users))
        self.assertEquals(1, len([u for u in test_users if u.get('graph_user_data') and u.get('graph_permission_data')]))
        self.assertEquals(1, len([u for u in api_test_users if 'id' in u and u['id'] == test_users[0]['graph_user_data']['id']]))
        for permission in test_users[0]['permissions']:
            self.assertTrue(permission.strip() in test_users[0]['graph_permission_data']['data'][0])

        # Make sure the test user's information in Fandjango is correct
        self.assertEquals(1, User.objects.count())
        user = User.objects.get()
        self.assertTrue(user.is_test_user)
        self.assertEquals(test_users[0]['graph_user_data']['id'], str(user.facebook_id))
        self.assertEquals(test_users[0]['graph_user_data']['name'], user.full_name)

    def test_delete_one_user(self):
        pass

    def test_creating_many_users(self):
        from mock_django.testapp2.facebook_test_users import facebook_test_users
        facebook_test_users = facebook_test_users()
        self.assertEquals(0, User.objects.count())
        app_access_token = '%s|%s' % (FACEBOOK_APPLICATION_ID, FACEBOOK_APPLICATION_SECRET_KEY)

        management.call_command('create_facebook_test_users', 'testapp2', allow_duplicate_users=True)

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (FACEBOOK_APPLICATION_ID, app_access_token)
        test_users = merge_with_facebook_data(facebook_test_users,
                                              json.loads(requests.get(test_users_url).content)['data'],
                                              app_access_token)

        # Make sure each test user's information on facebook is correct
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])

        # Make sure each test user's information in Fandjango is correct
        self.assertEquals(3, User.objects.count())
        for user in User.objects.all():
            test_user = [t for t in test_users if t['graph_user_data']['id'] == str(user.facebook_id)][0]
            self.assertTrue(user.is_test_user)
            self.assertEquals(test_user['name'], user.full_name)

    def test_overwriting_many_users(self):
        from mock_django.testapp2.facebook_test_users import facebook_test_users
        facebook_test_users = facebook_test_users()
        self.assertEquals(0, User.objects.count())
        app_access_token = '%s|%s' % (FACEBOOK_APPLICATION_ID, FACEBOOK_APPLICATION_SECRET_KEY)

        management.call_command('create_facebook_test_users', 'testapp2', allow_duplicate_users=True)
        management.call_command('create_facebook_test_users', 'testapp2')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (FACEBOOK_APPLICATION_ID, app_access_token)
        test_users = merge_with_facebook_data(facebook_test_users,
                                              json.loads(requests.get(test_users_url).content)['data'],
                                              app_access_token)

        # Make sure each test user's information on facebook is correct
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])

        # Make sure each test user's information in Fandjango is correct
        self.assertEquals(3, User.objects.count())
        for user in User.objects.all():
            test_user = [t for t in test_users if t['graph_user_data']['id'] == str(user.facebook_id)][0]
            self.assertTrue(user.is_test_user)
            self.assertEquals(test_user['name'], user.full_name)

    def test_deleting_many_users(self):
        pass

    def test_creating_users_with_friends(self):
        pass

    def test_deleting_users_with_friends(self):
        pass

def merge_with_facebook_data(facebook_test_users, graph_test_users, access_token):
    """
    Creates a copy of the facebook_test_users dictionary, attaching each test user's user and permission data
    from the open graph api.
    """
    # Merge open graph data with the original facebook_test_users dictionary
    facebook_test_users = copy.deepcopy(facebook_test_users)
    for graph_test_user in graph_test_users:
        if 'id' in graph_test_user:
            facebook_id = graph_test_user['id']
            test_user_url = "https://graph.facebook.com/%s?access_token=%s" % (facebook_id, access_token)
            permissions_url = "https://graph.facebook.com/%s/permissions?access_token=%s" % (facebook_id, access_token)
            user_data = json.loads(requests.get(test_user_url).content)
            permissions_data = json.loads(requests.get(permissions_url).content)

            for facebook_test_user in facebook_test_users:
                if user_data and 'name' in user_data and facebook_test_user['name'] == user_data['name']:
                    facebook_test_user['graph_user_data'] = user_data
                    facebook_test_user['graph_permission_data'] = permissions_data if 'data' in permissions_data else None

    # Remove any test users that didn't recieve any data from open graph
    test_users = []
    for test_user in facebook_test_users:
        if 'graph_user_data' in test_user and 'graph_permission_data' in test_user:
            test_users.append(test_user)

    return test_users