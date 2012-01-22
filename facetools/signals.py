import django.dispatch

sync_facebook_test_user = django.dispatch.Signal(providing_args=["test_user"])
setup_facebook_test_client = django.dispatch.Signal(providing_args=["client, signed_request"])