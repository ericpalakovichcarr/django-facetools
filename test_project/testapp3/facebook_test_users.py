def facebook_test_users():
    return [
        {
            'name': 'Unittest Jacobs',
            'installed': False,
            'permissions': [],
            'friends': []
        },
        {
            'name': 'Unittest Deschain',
            'installed': True,
            'permissions': [],
            'friends': ['Unittest Billows']
        },
        {
            'name': 'Unittest Billows',
            'installed': True,
            'permissions': [],
            'friends': ['Unittest Deschain']
        },
    ]
