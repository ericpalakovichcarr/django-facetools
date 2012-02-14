from django.db import models

class TestUser(models.Model):
    """
    A test user on facebook.
    """
    name = models.CharField(max_length=255, primary_key=True)
    facebook_id = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    login_url = models.CharField(max_length=255, null=True, blank=True)

    def delete(self, *args, **kwargs):
        from facetools.test.testusers import _delete_test_user_on_facebook # avoiding circular dependency
        if self.facebook_id:
            for attempts in range(3, 0, -1):
                try:
                    _delete_test_user_on_facebook(self)
                    break
                except:
                    if attempts <= 0:
                        raise
        super(TestUser, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name

