import os
from facetools import json
import copy
import datetime

import requests
from django.test import TestCase
from django.core import management
from django.conf import settings
from fandjango.models import User

from facetools.management.commands.sync_facebook_test_users import _get_test_user_relationships
from facetools.common import _get_app_access_token
from facetools.test.testusers import _delete_test_user_on_facebook
from facetools.models import TestUser
from facetools.management.commands.sync_facebook_test_users import _get_app_fixture_directory, _get_facetools_test_fixture_name, _clean_test_user_fixture
from facetools.signals import sync_facebook_test_user
from facetools.integrations import fandjango
from test_project import testapp1, testapp2, testapp3

class SyncFacebookTestUsersTests(TestCase):

    def tearDown(self):
        for test_user in TestUser.objects.all():
            test_user.delete() # should also delete facebook test user through delete method override

    def assertAccessTokenExpirationDate(self, facebook_user):
        self.assertTrue(facebook_user.access_token_expires - datetime.datetime.now() > datetime.timedelta(days=5))

    def test_get_test_user_relationships(self):
        t1 = [{'name': 'Unittest Jacobs', 'friends': ['Unittest Deschain','Unittest Billows']},
              {'name': 'Unittest Deschain', 'friends': ['Unittest Jacobs','Unittest Billows']},
              { 'name': 'Unittest Billows', 'friends': ['Unittest Deschain', 'Unittest Jacobs']}]
        t2 = [{'name': 'Unittest Jacobs', 'friends': ['Unittest Deschain']},
              {'name': 'Unittest Deschain', 'friends': ['Unittest Jacobs']},
              { 'name': 'Unittest Billows', 'friends': ['Unittest Deschain', 'Unittest Jacobs']}]
        t3 = [{'name': 'Unittest Jacobs', 'friends': ['Unittest Deschain']},
              {'name': 'Unittest Deschain', 'friends': []},
              { 'name': 'Unittest Billows', 'friends': ['Unittest Deschain', 'Unittest Jacobs']}]
        t4 = [{'name': 'Unittest Jacobs', 'friends': []},
              {'name': 'Unittest Deschain', 'friends': ['Unittest Jacobs']},
              { 'name': 'Unittest Billows', 'friends': ['Unittest Deschain', 'Unittest Jacobs']}]
        t5 = [{'name': 'Unittest Jacobs', 'friends': ['Unittest Billows']},
              {'name': 'Unittest Deschain', 'friends': ['Unittest Jacobs']},
              { 'name': 'Unittest Billows', 'friends': ['Unittest Deschain']}]

        for t in [t1,t2,t3,t4,t5]:
            relationships = _get_test_user_relationships(t)
            self.assertEquals(3, len(relationships))
            self.assertTrue((set([t[0]['name'], t[1]['name']])) in relationships)
            self.assertTrue((set([t[0]['name'], t[2]['name']])) in relationships)
            self.assertTrue((set([t[1]['name'], t[2]['name']])) in relationships)

    def test_creating_one_user(self):
        from test_project.testapp1.facebook_test_users import facebook_test_users
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp1')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (
            settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        api_test_users = json.loads(requests.get(test_users_url).content)['data']
        test_users = _merge_with_facebook_data(facebook_test_users, api_test_users, _get_app_access_token())

        # Make sure the test user's information on facebook is correct
        self.assertEquals(1, len(test_users))
        self.assertEquals(1, len([u for u in test_users if u.get('graph_user_data') and u.get('graph_permission_data')]))
        for permission in test_users[0]['permissions']:
            self.assertTrue(permission.strip() in test_users[0]['graph_permission_data']['data'][0])

        # Make sure the test user's information in facetools is correct
        self.assertEquals(1, TestUser.objects.count())
        user = TestUser.objects.get()
        self.assertEquals(int(test_users[0]['graph_user_data']['id']), user.facebook_id)
        self.assertEquals(test_users[0]['name'], user.name)
        self.assertEquals(test_users[0]['graph_user_data']['login_url'], user.login_url)
        self.assertEquals(test_users[0]['installed'], _has_access_code(user.access_token))
        self.assertAccessTokenExpirationDate(user)

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp1, 'testapp1', facebook_test_users)

    def test_overwrite_one_user(self):
        from test_project.testapp1.facebook_test_users import facebook_test_users
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp1')
        management.call_command('sync_facebook_test_users', 'testapp1')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (
            settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        api_test_users = json.loads(requests.get(test_users_url).content)['data']
        test_users = _merge_with_facebook_data(facebook_test_users, api_test_users, _get_app_access_token())

        # Make sure the test user's information on facebook is correct
        self.assertEquals(1, len(test_users))
        self.assertEquals(1, len([u for u in test_users if u.get('graph_user_data') and u.get('graph_permission_data')]))
        self.assertEquals(1, len([u for u in api_test_users if 'id' in u and u['id'] == test_users[0]['graph_user_data']['id']]))
        for permission in test_users[0]['permissions']:
            self.assertTrue(permission.strip() in test_users[0]['graph_permission_data']['data'][0])

        # Make sure the test user's information in facetools is correct
        self.assertEquals(1, TestUser.objects.count())
        user = TestUser.objects.get()
        self.assertEquals(int(test_users[0]['graph_user_data']['id']), user.facebook_id)
        self.assertEquals(test_users[0]['graph_user_data']['name'], user.name)
        self.assertEquals(test_users[0]['graph_user_data']['login_url'], user.login_url)
        self.assertEquals(test_users[0]['installed'], _has_access_code(user.access_token))
        self.assertAccessTokenExpirationDate(user)

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp1, 'testapp1', facebook_test_users)

    def test_creating_many_users(self):
        from test_project.testapp2.facebook_test_users import facebook_test_users as t2
        facebook_test_users = t2()
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp2')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure each test user's information on facebook is correct
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])
            friends_on_facebook = _get_friends_on_facebook(test_user)
            for friend_name in test_user.get('friends', []):
                self.assertTrue(friend_name in friends_on_facebook)
                self.assertEqual(friends_on_facebook[friend_name],
                                 TestUser.objects.get(name=friend_name).facebook_id)

        # Make sure each test user's information in facetools is correct
        self.assertEquals(3, TestUser.objects.count())
        for user in TestUser.objects.all():
            test_user = [t for t in test_users if int(t['graph_user_data']['id']) == user.facebook_id][0]
            self.assertEquals(test_user['name'], user.name)
            self.assertEquals(test_user['graph_user_data']['login_url'], user.login_url)
            self.assertEquals(test_user['installed'], _has_access_code(user.access_token))
            self.assertAccessTokenExpirationDate(user)

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp2, 'testapp2', t2())

    def test_overwriting_many_users(self):
        from test_project.testapp2.facebook_test_users import facebook_test_users as t2
        facebook_test_users = t2()
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp2')
        management.call_command('sync_facebook_test_users', 'testapp2')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure each test user's information on facebook is correct
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])
            friends_on_facebook = _get_friends_on_facebook(test_user)
            for friend_name in test_user.get('friends', []):
                self.assertTrue(friend_name in friends_on_facebook)
                self.assertEqual(friends_on_facebook[friend_name],
                                 TestUser.objects.get(name=friend_name).facebook_id)


        # Make sure each test user's information in facetools is correct
        self.assertEquals(3, TestUser.objects.count())
        for user in TestUser.objects.all():
            test_user = [t for t in test_users if t['graph_user_data']['id'] == str(user.facebook_id)][0]
            self.assertEquals(test_user['name'], user.name)
            self.assertEquals(test_user['graph_user_data']['login_url'], user.login_url)
            self.assertEquals(test_user['installed'], _has_access_code(user.access_token))
            self.assertAccessTokenExpirationDate(user)

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp2, 'testapp2', t2())

    def test_creating_many_users_mixed_installations(self):
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t3()
        self.assertTrue(not all([u['installed'] for u in facebook_test_users])) # make sure all the users aren't set to have the app installed
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp3')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure each test user's information on facebook is correct
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])
            friends_on_facebook = _get_friends_on_facebook(test_user)
            for friend_name in test_user.get('friends', []):
                self.assertTrue(friend_name in friends_on_facebook)
                self.assertEqual(friends_on_facebook[friend_name],
                                 TestUser.objects.get(name=friend_name).facebook_id)

        # Make sure each test user's information in facetools is correct
        self.assertEquals(3, TestUser.objects.count())
        for user in TestUser.objects.all():
            test_user = [t for t in test_users if int(t['graph_user_data']['id']) == user.facebook_id][0]
            self.assertEquals(test_user['name'], user.name)
            self.assertEquals(test_user['graph_user_data']['login_url'], user.login_url)
            self.assertEquals(test_user['installed'], _has_access_code(user.access_token))
            self.assertAccessTokenExpirationDate(user)

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp3, 'testapp3', t3())

    def test_overwriting_many_users_mixed_installations(self):
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t3()
        self.assertTrue(not all([u['installed'] for u in facebook_test_users])) # make sure all the users aren't set to have the app installed
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp3')
        management.call_command('sync_facebook_test_users', 'testapp3')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure each test user's information on facebook is correct
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])
            friends_on_facebook = _get_friends_on_facebook(test_user)
            for friend_name in test_user.get('friends', []):
                self.assertTrue(friend_name in friends_on_facebook)
                self.assertEqual(friends_on_facebook[friend_name],
                                 TestUser.objects.get(name=friend_name).facebook_id)

        # Make sure each test user's information in facetools is correct
        self.assertEquals(3, TestUser.objects.count())
        for user in TestUser.objects.all():
            test_user = [t for t in test_users if t['graph_user_data']['id'] == str(user.facebook_id)][0]
            self.assertEquals(test_user['name'], user.name)
            self.assertEquals(test_user['graph_user_data']['login_url'], user.login_url)
            self.assertEquals(test_user['installed'], _has_access_code(user.access_token))
            self.assertAccessTokenExpirationDate(user)

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp3, 'testapp3', t3())

    def test_sync_where_in_facetools_missing_in_facebook(self):
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t3()
        self.assertTrue(not all([u['installed'] for u in facebook_test_users])) # make sure all the users aren't set to have the app installed
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp3')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure the data looks good
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u]))

        # Now remove the users from facebook, leaving them in facetools database
        for test_user in test_users:
            _delete_test_user_on_facebook(TestUser.objects.get(name=test_user['name']))
        self.assertEquals(3, TestUser.objects.count())
        check_users = json.loads(requests.get(test_users_url).content)['data']
        old_ids = [u['graph_user_data']['id'] for u in test_users]
        self.assertTrue(not any([c['id'] in old_ids for c in check_users]))

        # After syncing again the data should be back to normal
        management.call_command('sync_facebook_test_users', 'testapp3')
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u]))

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp3, 'testapp3', t3())

    def test_sync_where_in_facebook_missing_in_facetools(self):
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t3()
        self.assertTrue(not all([u['installed'] for u in facebook_test_users])) # make sure all the users aren't set to have the app installed
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp3')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure the data looks good
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u]))

        # Now remove the users from facetools, leaving them on facebook
        TestUser.objects.all().delete()
        self.assertEquals(0, TestUser.objects.count())
        check_users = json.loads(requests.get(test_users_url).content)['data']
        old_ids = [u['graph_user_data']['id'] for u in test_users]
        self.assertEquals(3, len([c for c in check_users if c['id'] in old_ids]))

        # After syncing again the data should be back to normal
        management.call_command('sync_facebook_test_users', 'testapp3')
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u]))

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp3, 'testapp3', t3())

    def test_sync_where_in_facebook_and_in_facetools_but_data_not_synced(self):
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t3()
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp3')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure the data looks good
        self.assertEquals(3, TestUser.objects.count())
        self.assertEquals(3, len(test_users))
        self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u]))

        # Now change the user data on facetools, leaving them out of sync with the facebook data
        old_values = {}
        try:
            for test_user in TestUser.objects.all():
                old_values[test_user.name] = {
                    'facebook_id': test_user.facebook_id,
                    'access_token': test_user.access_token
                }
                test_user.facebook_id = 0
                test_user.access_token = "failbear"
                test_user.save()

            # After syncing again the data should be back to normal
            management.call_command('sync_facebook_test_users', 'testapp3')
            test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())
            self.assertEquals(3, TestUser.objects.count())
            self.assertEquals(3, len(test_users))
            self.assertEquals(3, len([u for u in test_users if 'graph_user_data' in u]))
            for test_user in TestUser.objects.all():
                self.assertNotEquals(0, test_user.facebook_id)
                self.assertNotEquals("failbear", test_user.access_token)
        finally:
            for test_user in TestUser.objects.all():
                test_user.facebook_id = old_values[test_user.name]['facebook_id']
                test_user.access_token = old_values[test_user.name]['access_token']
                test_user.save()

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp3, 'testapp3', t3())

    def test_sync_multiple_apps(self):
        from test_project.testapp1.facebook_test_users import facebook_test_users as t1
        from test_project.testapp2.facebook_test_users import facebook_test_users as t2
        facebook_test_users = t1 + t2()
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users', 'testapp1', 'testapp2')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure each test user's information on facebook is correct
        self.assertEquals(4, len(test_users))
        self.assertEquals(4, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])
            friends_on_facebook = _get_friends_on_facebook(test_user)
            for friend_name in test_user.get('friends', []):
                self.assertTrue(friend_name in friends_on_facebook)
                self.assertEqual(friends_on_facebook[friend_name],
                                 TestUser.objects.get(name=friend_name).facebook_id)

        # Make sure each test user's information in facetools is correct
        self.assertEquals(4, TestUser.objects.count())
        for user in TestUser.objects.all():
            test_user = [t for t in test_users if int(t['graph_user_data']['id']) == user.facebook_id][0]
            self.assertEquals(test_user['name'], user.name)
            self.assertEquals(test_user['graph_user_data']['login_url'], user.login_url)
            self.assertEquals(test_user['installed'], _has_access_code(user.access_token))

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp1, 'testapp1', t1)
        self.assertTestUserFixture(testapp2, 'testapp2', t2())

    def test_sync_all_apps(self):
        from test_project.testapp1.facebook_test_users import facebook_test_users as t1
        from test_project.testapp2.facebook_test_users import facebook_test_users as t2
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t1 + t2() + t3()
        self.assertEquals(0, TestUser.objects.count())
        management.call_command('sync_facebook_test_users')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure each test user's information on facebook is correct
        self.assertEquals(7, len(test_users))
        self.assertEquals(7, len([u for u in test_users if 'graph_user_data' in u and 'graph_permission_data' in u]))
        for test_user in test_users:
            for permission in test_user['permissions']:
                self.assertTrue(permission.strip() in test_user['graph_permission_data']['data'][0])
            friends_on_facebook = _get_friends_on_facebook(test_user)
            for friend_name in test_user.get('friends', []):
                self.assertTrue(friend_name in friends_on_facebook)
                self.assertEqual(friends_on_facebook[friend_name],
                                 TestUser.objects.get(name=friend_name).facebook_id)

        # Make sure each test user's information in facetools is correct
        self.assertEquals(7, TestUser.objects.count())
        for user in TestUser.objects.all():
            test_user = [t for t in test_users if int(t['graph_user_data']['id']) == user.facebook_id][0]
            self.assertEquals(test_user['name'], user.name)
            self.assertEquals(test_user['graph_user_data']['login_url'], user.login_url)
            self.assertEquals(test_user['installed'], _has_access_code(user.access_token))

        # Make sure the generated fixture is correct
        self.assertTestUserFixture(testapp1, 'testapp1', t1)
        self.assertTestUserFixture(testapp2, 'testapp2', t2())
        self.assertTestUserFixture(testapp3, 'testapp3', t3())

    def assertTestUserFixture(self, app, app_name, test_users):
        fixture_file_path = os.path.join(_get_app_fixture_directory(app),
                                         _get_facetools_test_fixture_name(app_name))
        fixture_test_users = json.loads(open(fixture_file_path).read())
        fixture_user_names = set([u['pk'] for u in fixture_test_users])
        expected_user_names = set([u['name'] for u in test_users])
        self.assertEquals(expected_user_names, fixture_user_names)

class FixTestUserFixtureTests(TestCase):

    def test_clean_test_user_fixture_1(self):
        fixture_content = """[
    {
        "pk": "Unittest Smith",
        "model": "facetools.testuser",
        "fields": {
            "access_token": "AAAESR2HSywMBAAZBgFVWohGpg0XtALkfga09fF4mZBwhtF2q0ORpYJ7tJdZBEj5cWw8wQzbMcZBZBFZAZBVuFnAIV7JxBaZAUAOOBa5a7e4Qrav5ZCndFWDmA",
            "login_url": "https://www.facebook.com/platform/test_account_login.php?user_id=100003568662664&n=rx3Yb9ihtNlVHfT",
            "facebook_id": "100003568662664"
        }
    },
    {
        "pk": "Unittest Jacobs",
        "model": "facetools.testuser",
        "fields": {
            "access_token": "AAAESR2HSywMBAGQu1lzfZABZCCMq81JFPx4PP2KzR1IsLO7nZBTZCGU1szsdH2nn4aNmZB5FcvJcEDyv8Et9P8TDurZA2K522oJcYFEtETIAq6NrmKLbZBR",
            "login_url": "https://www.facebook.com/platform/test_account_login.php?user_id=100003573522566&n=PB5kX2MF0VUJ2mn",
            "facebook_id": "100003573522566"
        }
    }
]"""
        expected_content = """[
    {
        "pk": "Unittest Jacobs",
        "model": "facetools.testuser",
        "fields": {
            "access_token": "AAAESR2HSywMBAGQu1lzfZABZCCMq81JFPx4PP2KzR1IsLO7nZBTZCGU1szsdH2nn4aNmZB5FcvJcEDyv8Et9P8TDurZA2K522oJcYFEtETIAq6NrmKLbZBR",
            "login_url": "https://www.facebook.com/platform/test_account_login.php?user_id=100003573522566&n=PB5kX2MF0VUJ2mn",
            "facebook_id": "100003573522566"
        }
    }
]"""
        test_users = [
            {
                'name': 'Unittest Jacobs',
                'installed': True,
                'permissions': []
            }
        ]

        new_content = _clean_test_user_fixture(fixture_content, test_users)
        self.assertEquals(expected_content, new_content)

    def test_clean_test_user_fixture_2(self):
        fixture_content = """[
    {
        "pk": "Unittest Smith",
        "model": "facetools.testuser",
        "fields": {
            "access_token": "AAAESR2HSywMBAAZBgFVWohGpg0XtALkfga09fF4mZBwhtF2q0ORpYJ7tJdZBEj5cWw8wQzbMcZBZBFZAZBVuFnAIV7JxBaZAUAOOBa5a7e4Qrav5ZCndFWDmA",
            "login_url": "https://www.facebook.com/platform/test_account_login.php?user_id=100003568662664&n=rx3Yb9ihtNlVHfT",
            "facebook_id": "100003568662664"
        }
    },
    {
        "pk": "Unittest Jacobs",
        "model": "facetools.testuser",
        "fields": {
            "access_token": "AAAESR2HSywMBAGQu1lzfZABZCCMq81JFPx4PP2KzR1IsLO7nZBTZCGU1szsdH2nn4aNmZB5FcvJcEDyv8Et9P8TDurZA2K522oJcYFEtETIAq6NrmKLbZBR",
            "login_url": "https://www.facebook.com/platform/test_account_login.php?user_id=100003573522566&n=PB5kX2MF0VUJ2mn",
            "facebook_id": "100003573522566"
        }
    }
]"""
        expected_content = """[
    {
        "pk": "Unittest Smith",
        "model": "facetools.testuser",
        "fields": {
            "access_token": "AAAESR2HSywMBAAZBgFVWohGpg0XtALkfga09fF4mZBwhtF2q0ORpYJ7tJdZBEj5cWw8wQzbMcZBZBFZAZBVuFnAIV7JxBaZAUAOOBa5a7e4Qrav5ZCndFWDmA",
            "login_url": "https://www.facebook.com/platform/test_account_login.php?user_id=100003568662664&n=rx3Yb9ihtNlVHfT",
            "facebook_id": "100003568662664"
        }
    }
]"""
        test_users = [
            {
                'name': 'Unittest Smith',
                'installed': True,
                'permissions': []
            }
        ]

        new_content = _clean_test_user_fixture(fixture_content, test_users)
        self.assertEquals(expected_content, new_content)

class FandjangoIntegrationTest(TestCase):
    fixtures = ['fandjango_users_testapp3']

    def _pre_setup(self):
        sync_facebook_test_user.connect(fandjango.sync_facebook_test_user)
        super(FandjangoIntegrationTest, self)._pre_setup()

    def _post_teardown(self):
        sync_facebook_test_user.disconnect(fandjango.sync_facebook_test_user)
        super(FandjangoIntegrationTest, self)._post_teardown()

    def tearDown(self):
        for test_user in TestUser.objects.all():
            test_user.delete() # should also delete facebook test user through delete method override

    def test_fandjango_users_created_correctly(self):
        from test_project.testapp3.facebook_test_users import facebook_test_users as t3
        facebook_test_users = t3()
        self.assertTrue(not all([u['installed'] for u in facebook_test_users])) # make sure all the users aren't set to have the app installed
        management.call_command('sync_facebook_test_users', 'testapp3')

        # Get the test user data from facebook
        test_users_url = "https://graph.facebook.com/%s/accounts/test-users?access_token=%s" % (settings.FACEBOOK_APPLICATION_ID, _get_app_access_token())
        test_users = _merge_with_facebook_data(facebook_test_users, json.loads(requests.get(test_users_url).content)['data'], _get_app_access_token())

        # Make sure only the test users that have the app installed have correpsonding Fandjango User records
        self.assertEquals(3, User.objects.count())
        for test_user in test_users:
            user = User.objects.get(facebook_id=int(test_user['graph_user_data']['id']))
            self.assertEquals(test_user['installed'], user.authorized)
            if test_user['installed']:
                self.assertEquals(test_user['access_token'], user.oauth_token.token)
            else:
                self.assertEquals("", user.oauth_token.token)

def _merge_with_facebook_data(facebook_test_users, graph_test_users, access_token):
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
                    facebook_test_user['access_token'] = graph_test_user.get('access_token')
                    facebook_test_user['graph_user_data'] = user_data
                    facebook_test_user['graph_user_data']['login_url'] = graph_test_user['login_url']
                    facebook_test_user['graph_permission_data'] = permissions_data if 'data' in permissions_data else None

    # Remove any test users that didn't recieve any data from open graph
    test_users = []
    for test_user in facebook_test_users:
        if 'graph_user_data' in test_user and 'graph_permission_data' in test_user:
            test_users.append(test_user)

    return test_users

def _has_access_code(access_code):
    return access_code is not None and len(access_code) > 0

def _get_friends_on_facebook(test_user):
    friends_url = "https://graph.facebook.com/%s/friends?access_token=%s" % (test_user['graph_user_data']['id'], _get_app_access_token())
    friends_data = json.loads(requests.get(friends_url).content)
    friends = {}
    if type(friends_data) is not bool and 'data' in friends_data:
        for friend in friends_data['data']:
            friends[friend['name']] = int(friend['id'])
        assert len(friends) == len(friends_data['data'])
    return friends
