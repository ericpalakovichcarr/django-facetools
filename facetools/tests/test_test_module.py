import datetime
from fandjango.test import FacebookTestCase

class TestFacebookTestCase(FacebookTestCase):
    pass

def test_name_to_test_user():
    from fandjango.models import User, OAuthToken
    from fandjango.test.common import _name_to_test_user
    names_to_test = [
        ['Trey David Smith', ['Trey', 'David', 'Smith']],
        ['Trey Smith', ['Trey', None, 'Smith']],
        ['Trey', ['Trey', None, 'Trey']], # facebook takes one word names for the first and last name of a test user
    ]
    try:
        for name_to_test in names_to_test:
            u = User.objects.create(
                facebook_id = -1,
                first_name=name_to_test[1][0],
                middle_name=name_to_test[1][1],
                last_name=name_to_test[1][2],
                is_test_user=True,
                oauth_token=OAuthToken.objects.create(token="", issued_at=datetime.datetime.now())
            )
            assert u.id == _name_to_test_user(name_to_test[0]).id
        for u in User.objects.all():
            assert u == _name_to_test_user(u)
    finally:
        for u in User.objects.all():
            u.delete()
        for t in OAuthToken.objects.all():
            t.delete()

def test_get_relationships():
    from fandjango.test.common import _get_relationships
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
        relationships = _get_relationships(t)
        assert 3 == len(relationships)
        assert (set([t[0]['name'], t[1]['name']])) in relationships
        assert (set([t[0]['name'], t[2]['name']])) in relationships
        assert (set([t[1]['name'], t[2]['name']])) in relationships