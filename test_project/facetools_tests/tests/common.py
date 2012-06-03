import json

from facetools import settings
import requests

def delete_all_test_users():
    existing_test_users = facebook_request("https://graph.facebook.com/%s/accounts/test-users?access_token=%s|%s" % (
        settings.FACEBOOK_APPLICATION_ID,
        settings.FACEBOOK_APPLICATION_ID,
        settings.FACEBOOK_APPLICATION_SECRET_KEY)
    )["data"]
    for test_user in existing_test_users:
        facebook_request("https://graph.facebook.com/%s/?method=delete&access_token=%s|%s" % (
            test_user["id"],
            settings.FACEBOOK_APPLICATION_ID,
            settings.FACEBOOK_APPLICATION_SECRET_KEY
        ))

def facebook_request(url, method="GET", num_attempts=settings.FACETOOLS_NUM_REQUEST_ATTEMPTS, request_timeout=settings.FACETOOLS_REQUEST_TIMEOUT, exc_type=Exception):
    method = method.lower()
    if method not in dir(requests):
        raise ValueError("%s is an usupported method.  Try HEAD, GET, POST, PUT, or DELETE" % method)

    for attempts in range(num_attempts, 0, -1):
        response = getattr(requests, method)(url, timeout=request_timeout)
        try: data = json.loads(response.content)
        except: data = None
        if response.status_code != 200 or data is None or data == False or 'error' in data:
            if attempts > 1:
                continue
            try:
                error_message = data['error']['message']
            except:
                error_message = None

            if error_message:
                raise exc_type(error_message)
            else:
                raise exc_type("Request to facebook failed (status_code=%s and content=\"%s\")" % (response.status_code, response.content))
        break
    else:
        raise exc_type("Request to facebook failed")

    return data