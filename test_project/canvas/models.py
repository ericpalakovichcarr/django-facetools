from django.db import models
from django.core.urlresolvers import reverse

class ModelForTests(models.Model):
    """
    Used for testing fb_redirect function, which takes an model instsance and
    gets it's url from it's get_absolute_url method.  It's also used in a test
    view to test other url resolve code that requires a model.
    """
    def get_absolute_url(self):
        return reverse('canvas:test_model', args=[self.id])
