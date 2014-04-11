skytruth-automation-hub
=======================

A simple set of google app engine services to support distributed automation.  Includes a simple task queue, publish/subscribe and a spatially aware data feed (geofeed)


**[Design Notes] (./design_notes.md)**

**[RoadMap] (./roadmap.md)**

MAVERICKS
=========

The compiler in Mavericks has deprecated specific flags, which can have problems compiling Python modules with C extension, so do the following before moving to the INSTALL section
    export CFLAGS=-Qunused-arguments
    export CPPFLAGS=-Qunused-arguments

Remember to `sudo -E` to load environment variables if doing `sudo pip install`

INSTALL
=======

First, make yourself a virtual env, and then 
    pip install -r requirements.txt

Before you can run the unit tests, you must copy settings-template.py to settings.py and edit the content

Once that's done, you're ready to test and deploy


Unit Tests
==========

In order to run the tests, you have to have a dev server up and running at http://localhost:8080

Once the server is started, you can run all the tests from the gae directory with 

    nosetests --with-gae


Authentication
==============

See HowTo-Authentication.txt for details on setting up authentication

Note that you can disable authentication by setting ENFORCE_AUTH in settings.py

You cannot test authenticaion with the dev server, so when running on the dev server, authentication is disabled automatically in settings.py so that the unit tests will run successfully.

To test authentication, you have to run against a live instance in Google App Engine. To do this, deploy the app to GAE, and then use smoketest.py to validate that everything works.

    python smoketest.py https://skytruth-bot-tasks.appspot.com privatekey.pem SOMETHING@developer.gserviceaccount.com 

Note that the email address you pass in to the smoke test much match up with one of the CLIENT IDS in the allowed_client_ids property in the api declaraton in geofeed_api.py and taskqueue_api.py
