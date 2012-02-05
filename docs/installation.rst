Installing Django Facetools
***************************

Install Dependencies
====================

Django Facetools has been tested on Python 2.6 and 2.7.  It's been ran
using the following packages:

- Django >= 1.3.1
- south >= 0.7.3
- requests >= 0.7.3

To install these dependencies, you can use ``pip``::

    $ pip install django
    $ pip install south
    $ pip install requests

Install Django Facetools
========================

For the latest stable version (recommended), use ``pip`` or ``easy_install``::

    $ pip install django-facetools

**Alternatively**, you can also download the latest development version from
http://github.com/bigsassy/django-facetools and run the installation script::

    $ python setup.py install

**or** use ``pip``::

    $ pip install -e git://github.com/bigsassy/django-facetools#egg=django-facetools


Configure Django
================

- In your project settings, add ``facetools`` to the ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        # ... your other apps here
        'facetools',
    )

- Also set the ``FACEBOOK_APPLICATION_ID``, ``FACEBOOK_APPLICATION_SECRET_KEY``,
  ``FACEBOOK_CANVAS_URL``. and ``FACEBOOK_CANVAS_PAGE`` settings::

    FACEBOOK_APPLICATION_ID = '301572769893123'
    FACEBOOK_APPLICATION_SECRET_KEY = '[insert your secret key]'
    FACEBOOK_CANVAS_URL = 'https://myapp.mycompany.com/canvas/'
    FACEBOOK_CANVAS_PAGE = 'http://apps.facebook.com/myapp'

