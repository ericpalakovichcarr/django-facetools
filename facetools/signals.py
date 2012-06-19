import django.dispatch

sync_facebook_test_user = django.dispatch.Signal(providing_args=["test_user"])