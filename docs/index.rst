Django Facetools Documentation
******************************

Introduction
==================================================

Django Facetools provides a set of features to ease development of Facecbook
canvas apps in a Django project.

Features:

* Replacement ``url`` template tag as well as ``reverse`` and ``redirecct_to``
  functions that convert an internal url into it's facebook canvas equivalent
  (ex: http://my_app.mycompany.com/canvas/my_view to https://apps.facebook.com/my_app/my_view)
* Ability to define facebook test users, their permissions, and their initial
  friends per app.  Management commands ``sync_facebook_test_users`` and
  ``delete_facebook_test_users`` let you recreate your test users in your
  facebook app with one call.
* ``FacebookTestCase`` can be used in place of Django's ``TestCase``. Just
  specify a test user, much like a fixture, and requests to the test client
  will contain a valid signed_request for the test user.

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   installation
   urls
   testusers
   testcase

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

