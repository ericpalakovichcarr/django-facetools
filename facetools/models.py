import requests
from django.db import models
from facetools.common import _get_app_access_token
from facetools import json

class DeleteTestUserError(Exception): pass

class TestUser(models.Model):
    """
    A test user on facebook.
    """
    name = models.CharField(max_length=255)
    facebook_id = models.CharField(max_length=255, null=True, blank=True)
    last_access_token = models.CharField(max_length=255, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.facebook_id:
            delete_url_template = "https://graph.facebook.com/%s?method=delete&access_token=%s"
            delete_user_url = delete_url_template % (self.facebook_id, _get_app_access_token())
            r = requests.delete(delete_user_url)
            try: rdata = json.loads(r.content)
            except: rdata = {}
            if r.status_code != 200:
                try:
                    raise DeleteTestUserError("Error deleting user %s (%s) from facebook: %s" % (self.name, self.facebook_id, json.loads(r.content)['error']['message']))
                except:
                    raise DeleteTestUserError("Error deleting user %s (%s) from facebook: %s" % (self.name, self.facebook_id, r.content))
            elif 'error' in rdata and 'message' in rdata['error']:
                raise DeleteTestUserError("Error deleting user %s (%s) from facebook: %s" % (self.name, self.facebook_id, json.loads(r.content)['error']['message']))

        super(TestUser, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name