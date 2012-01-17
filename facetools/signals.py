import django.dispatch

pre_create_facebook_test_user = django.dispatch.Signal(providing_args=["test_user"])
post_create_facebook_test_user = django.dispatch.Signal(providing_args=["test_user", "facebook_response_data"])

pre_delete_facebook_test_user = django.dispatch.Signal(providing_args=["test_user"])
post_delete_facebook_test_user = django.dispatch.Signal(providing_args=["test_user"])

pre_friend_test_users = django.dispatch.Signal(providing_args=["test_user_1" "test_user_2"])
post_friend_test_users = django.dispatch.Signal(providing_args=["test_user_1" "test_user_2"])
