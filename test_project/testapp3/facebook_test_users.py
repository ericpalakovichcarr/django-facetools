def facebook_test_users():
    return [
        {
            'name': 'Unittest More',
            'placeholder_facebook_id': 64,
            'installed': False,
            'permissions': [],
            'friends': []
        },
        {
            'name': 'Unittest Vanilla',
            'placeholder_facebook_id': 65,
            'installed': True,
            'permissions': [],
            'friends': ['Unittest Waffers']
        },
        {
            'name': 'Unittest Waffers',
            'placeholder_facebook_id': 66,
            'installed': True,
            'permissions': [],
            'friends': ['Unittest Vanilla']
        },
    ]
