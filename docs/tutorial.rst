Writing your first Django app...for Facebook!
*********************************************

Converting existing Django apps to work as a Facebook app can be very simple.
We're going to see how simple by converting the official Django tutorial app
to work on facebook.  You can view the tutorial at:

https://docs.djangoproject.com/en/1.3/intro/tutorial01/

Here's how we're going to modify the poll app:

* Add tests for the original views
* Convert the app so it works as a Facebook canvas app
* Let users post their vote to their walls
* Let users invite their friends to vote in the poll
* Add more tests to cover the new features

We'll be using `django-facetools` along with `fandjango` to make this happen.

Get the example app
===================

Download the app and it's dependencies
--------------------------------------

First things first. Clone this example app's starting point from github::

    $ git clone git://github.com/bigsassy/facetools-example.git
    $ cd facetools-example

**Optionally,** you can create a virtualenv for this app::

    $ virtualenv --no-site-packages virenv
    $ source virenv/bin/activate

Next, you'll want to install the requirements for facetools::

    $ pip install -r requirements.txt

Now let's create the database::

    $ cd mysite
    $ python manage.py syncdb

And finally, let's start the development server::

    $ python manage.py runserver

Setup the example app
=====================

Add some data to the application
--------------------------------
Let's create some test data.

* Go to http://localhost:8000/admin/
* Click the *+Add* button for Polls
* Set the question to *What's up?*
* Click the *Show* link next to Date Information.  Click the *Today* and *Now* link for *Date published*.
* Enter the choices *Not much*, and *The sky*.  Set each choice's *Votes* field to 0.
* Click *Save and add another*
* Repeat, but set the question to *What's going down?*, with the choices *Not much*, and *My cholesterol*, once again with 0 votes each.
* Click the *Save* button.

Manually test the application
-----------------------------

Ok, let's run the app through it's paces.  It's a simple polling app where
you can view a list of polls, vote in any of the polls, and view the results
of the poll.

Check the list page first by going to http://localhost:8000/polls/.  You
should see a bulleted list with a two polls, called *What's up?* and *What's going down?*.

Click on the *What's up?* poll to see its detail page.  We should see the
poll's title again, two radio buttons with the options *Not much* and *The sky*,
and finally a vote button.  Chooese *The sky* and click vote.

This should take you to a result page, once again showing the poll's title,
followed by a bulleted list of the two choices *Not much* and *The sky* with their votes,
and a link to vote again.

Add tests for the original views
================================

So with everything working, we're going to write some tests using Django's test client
for everything we just manually did. We'll be revisiting these tests when
we use facetools to inject facebook test users into the Django test client.

Fist, let's create a data fixture to run out tests against.  Stop the `runserver` command
and run the following::

    $ python manage.py dumpdata polls --indent=4 > polls/fixtures/polls.json

Now open `polls/tests.py` and make make it look like this::

    from django.core.urlresolvers import reverse
    from django.test import TestCase
    from django.test import LiveServerTestCase

    from polls.models import Poll

    from selenium import webdriver

    class ClientSideTests(LiveServerTestCase):
        fixtures = ['polls.json']

        @classmethod
        def setUpClass(cls):
            cls.driver = webdriver.Firefox()
            cls.driver.implicitly_wait(5)
            super(TestPollVoting, cls).setUpClass()

        @classmethod
        def tearDownClass(cls):
            cls.driver.quit()

        def setUp(self):
            self.base_url = self.live_server_url

        def test_poll_list_page(self):
            pass

        def test_poll_voting(self):
            pass

    class ServerSideTests(TestCase):
        fixtures = ['polls.json']

        def test_index(self):
            pass

        def test_detail(self):
            pass

        def test_results(self):
            pass


