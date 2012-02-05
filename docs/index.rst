Django Facetools Documentation
******************************

Introduction
==================================================

Django Facetools provides a set of features to ease development of Facecbook
canvas apps in a Django project.

Features:

* Replacement ``url`` template tag as well as the ``reverse`` function that convert
  an internal url into it's facebook canvas equivalent
  (ex: http://my_app.mycompany.com/canvas/my_view to https://apps.facebook.com/my_app/my_view)
* Ability to define facebook test users, their permissions, and their initial
  friends per app.  The management command ``sync_facebook_test_users`` lets you recreate
  your test users in your facebook app with one call.
* ``FacebookTestCase`` can be used in place of Django's ``TestCase``. Just
  specify a test user's name, much like a fixture, and the test client will mock
  Facebook requests to your canvas app, complete with a valid signed request for the
  specified test user.
* Integration with other facebook django packages, supporting the following (with more to come):
  * Fandjango (https://github.com/jgorset/fandjango)

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   installation
   tutorial

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
