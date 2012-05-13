from django.conf import settings

# Values corresponding to the fields found on your Facebook app's administration page:  https://developers.facebook.com/apps
FACEBOOK_APPLICATION_ID = getattr(settings, 'FACEBOOK_APPLICATION_ID')
FACEBOOK_APPLICATION_SECRET_KEY = getattr(settings, 'FACEBOOK_APPLICATION_SECRET_KEY')
FACEBOOK_APPLICATION_NAMESPACE = getattr(settings, 'FACEBOOK_APPLICATION_NAMESPACE')
FACEBOOK_APPLICATION_CANVAS_URL = getattr(settings, "FACEBOOK_APPLICATION_CANVAS_URL")
FACEBOOK_APPLICATION_CANVAS_PAGE = getattr(settings, "FACEBOOK_APPLICATION_CANVAS_PAGE")

# If a Graph API request fails, retry the request this many times
FACETOOLS_NUM_REQUEST_ATTEMPTS = getattr(settings, "FACETOOLS_NUM_REQUEST_ATTEMPTS", 3)

# The number of seconds for facetools to wait for a Graph API request
FACETOOLS_REQUEST_TIMEOUT = getattr(settings, "FACETOOLS_REQUEST_TIMEOUT", 5)