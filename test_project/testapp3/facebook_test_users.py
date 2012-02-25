def facebook_test_users():
    return [
        {
            'name': 'Unittest More',
            'installed': False,
            'permissions': [],
            'friends': []
        },
        {
            'name': 'Unittest Vanilla',
            'installed': True,
            'permissions': [],
            'friends': ['Unittest Waffers']
        },
        {
            'name': 'Unittest Waffers',
            'installed': True,
            'permissions': [],
            'friends': ['Unittest Vanilla']
        },
    ]
