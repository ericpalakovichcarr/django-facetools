import datetime
from django.db import models
from django.conf import settings

class TestUser(models.Model):
    """
    A test user on facebook.
    """
    name = models.CharField(max_length=255, primary_key=True)
    facebook_id = models.BigIntegerField(null=True, blank=True)
    placeholder_facebook_id = models.BigIntegerField(null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    access_token_expires = models.DateTimeField(null=True)
    login_url = models.CharField(max_length=255, null=True, blank=True)

    def delete(self, *args, **kwargs):
        from facetools.test.testusers import _delete_test_user_on_facebook # avoiding circular dependency
        if self.facebook_id:
            _delete_test_user_on_facebook(self)
        super(TestUser, self).delete(*args, **kwargs)

    def _populate_from_graph_data(self, facebook_data):
        ts2dt = lambda x: datetime.datetime.fromtimestamp(expires) if x != 0 else None
        self.name = facebook_data.get('name', self.name)
        self.facebook_id = facebook_data['id']
        self.access_token = facebook_data.get('access_token')
        self.access_token_expires = ts2dt(int(facebook_data.get('expires', 0)))
        self.login_url = facebook_data.get('login_url')

    def __unicode__(self):
        return self.name
