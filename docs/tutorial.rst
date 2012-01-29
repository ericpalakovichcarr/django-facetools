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

    class ServerSideTests(TestCase):
        fixtures = ['polls.json']

        def test_index(self):
            pass

        def test_detail(self):
            pass

        def test_voting(self):
            pass

        def test_results(self):
            pass

We're going to write some tests to ensure the website is functioning
correctly on the server.  Let's get some of the simple ones out of
the way, only checking for templates and valid context variables::

    def test_index(self):
        # The view should return a valid page with the correct template
        response = self.client.get(reverse("poll_index"))
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, "polls/index.html")
        self.assertIn('latest_poll_list', response.context)

        # The template should get all the polls in the database
        expected_polls = [p.pk for p in response.context['latest_poll_list']]
        actual_polls = [p.pk for p in Poll.objects.all()]
        self.assertEquals(set(expected_polls), set(actual_polls))

    def test_detail(self):
        expected_poll = Poll.objects.get(pk=1)

        # The view should return a valid page with the correct template
        response = self.client.get(reverse("poll_detail", args=[expected_poll.pk]))
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, "polls/detail.html")
        self.assertIn('poll', response.context)

        # The poll should be the correct poll
        actual_poll = response.context['poll']
        self.assertEquals(expected_poll.pk, actual_poll.pk)

    def test_results(self):
        expected_poll = Poll.objects.get(pk=1)

        # The view should return a valid page with the correct template
        response = self.client.get(reverse("poll_detail", args=[expected_poll.pk]))
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, "polls/detail.html")
        self.assertIn('poll', response.context)

        # The poll should be the correct poll
        actual_poll = response.context['poll']
        self.assertEquals(expected_poll.pk, actual_poll.pk)

Next we'll write a test to put the voting feature through its paces::

    def test_voting(self):
        poll = Poll.objects.get(pk=1)

        # Test initial data assumptions
        self.assertEquals(0, poll.choice_set.get(pk=1).votes)
        self.assertEquals(0, poll.choice_set.get(pk=2).votes)

        # Test voting a bunch of times
        self.vote_and_assert(poll, 1, {1: 1, 2: 0})
        self.vote_and_assert(poll, 1, {1: 2, 2: 0})
        self.vote_and_assert(poll, 2, {1: 2, 2: 1})
        self.vote_and_assert(poll, 1, {1: 3, 2: 1})
        self.vote_and_assert(poll, 2, {1: 3, 2: 2})

    def vote_and_assert(self, poll, choice_pk, expected_choice_votes):
        expected_redirect_url = reverse("poll_results", args=[poll.pk])
        response = self.client.post(reverse("poll_vote",
            kwargs={'poll_id': poll.pk}),
            {
                'poll_id': poll.pk,
                'choice': choice_pk
            }
        )

        # Make sure after voting the user is redirected to the results page
        self.assertEquals(302, response.status_code)
        self.assertTrue(response['Location'].endswith(expected_redirect_url))

        # Make sure that the votes in the database reflect the new vote
        for choice_pk,expected_votes in expected_choice_votes.items():
            choice = poll.choice_set.get(pk=choice_pk)
            self.assertEquals(expected_votes, choice.votes)

Time to make sure our tests are working.  Assuming your still in the
`mysite` directory on the command line, do the following::

    $ python manage.py test polls

And with that we have pretty good coverage of our views (front-end
is another story).  Now, let's get to the fun stuff.

Convert the app into a Facebook canvas app
==========================================

Create the facebook app
-----------------------

Now with that the tutorial app less of a trivial example, let's transform
this Django app into a Facebook app.  Let's get started.

Before we do anything, you should familiarize yourself with Facebook
canvas apps: http://developers.facebook.com/docs/guides/canvas/.

Next, go the the tutorial at http://developers.facebook.com/docs/appsonfacebook/tutorial/
and complete the sections *Creating your App* and *Configuring your App*, using the
following values for your app settings:

* App Display Name: Whatever you want
* App name space: Whatever you want
* Contact e-mail: Your e-mail address
* App Domain: Leave this blank for this tutorial
* Category: Leave it on Other

In the *Select how your app integrates with Facebook* section, click the checkmark
next to *App on Facebook*.  Next enter `https://localhost:8443` for the *Secure Canvas
URL*.  Facebook now require all canvas apps to be served via SSL, so we're going to
leave the *Canvas URL* setting blank.

Finally click the *Save changes* button to create your app!


Serve the facebook app from you development machine
---------------------------------------------------

We told facebook to access our app via https://localhost:8443.  Since Facebook
requires an SSL connection, we can't tell facebook to use our `manage.py runserver` instsance
at http://localhost:8000, since it's not secure.  We're going to get around this by
using an application called Stunnel, which will let us setup an SSL connection locally.

First install stunnel.

Next, Assuming your still in the `mysite` directory on the command line, run the following::

    $ cd ../stunnel_cfg
    $ stunnel dev_https
    $ cd ../mysite
    $ python manage.py runserver

If you open your browser to https://localhost:8443/polls/ you should get a warning
that the certificate is not secure.  Accept the certificate and you should see the
polls page.

Seperate your canvas app from the admin
---------------------------------------

Next, we want to make sure the admin section of our site isn't availalble
from the facebook app.  We're going to modify the root urls.py in the `mysite`
directory so the polls app is reached from /canvas/
(e.g. https:localhost:8443/canvas/polls/poll/1/)/  We're going to change
one line from this::

    url(r'^polls/', include('polls.urls')),

To this::

    url(r'^canvas/polls/', include('polls.urls')),

Now, let's run out tests to make sure everything is still working.  Close
the `runserver` command if it's still running and do the following::

    $ python manage.py test polls

Sure enough, all out tests still pass even after changing our url
structure.  This is because we used the `reverse` function in our
tests to get each view's url by name, instead of hardcoding them.
That's how we keep things DRY in Django.

Try out your Facebook app!
--------------------------

Ok, go to your app url.  First, bring your server back up::

    $ python manage.py runserver

Then open your facebook canvas app in your browser.  The url will be
something like https://apps.facebook.com/your-app-namespace.

** NOTES **

- Create middleware that automatically creates a top.location
  redirect for requests that came from a redirect to a canvas page.