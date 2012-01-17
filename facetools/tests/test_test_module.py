import datetime
from fandjango.test import FacebookTestCase

class TestFacebookTestCase(FacebookTestCase):
    pass

def test_get_test_user_relationships():
    from facetools.management.commands.create_facebook_test_users import get_test_user_relationships
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
        relationships = get_test_user_relationships(t)
        assert 3 == len(relationships)
        assert (set([t[0]['name'], t[1]['name']])) in relationships
        assert (set([t[0]['name'], t[2]['name']])) in relationships
        assert (set([t[1]['name'], t[2]['name']])) in relationships
