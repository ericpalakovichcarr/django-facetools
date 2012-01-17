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
http://github.com/philomat/django-facetools and run the installation script::

    $ python setup.py install

**or** use ``pip``::

    $ pip install -e git://github.com/philomat/django-facetools#egg=django-facetools


Configure Django
================

- In your project settings, add ``facetools`` to the ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        # ... your other apps here
        'facetools',
    )
