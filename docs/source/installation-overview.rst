.. _installation-overview:

========
Overview
========

.. _install-requirements:

Install requirements
====================

A Requirements file gives you a way to create an environment where you can put
all optional dependencies which are needed for your Project/Application.

To get started with Newfies-Dialer you must have the following installed:

- python >= 2.7 (programming language)
- HTTP server with WSGI modules (Apache, Nginx)
- Django Framework >= 1.6.1 (Python based Web framework)
- Celery >= 3.0 (Asynchronous task queue/job queue based on distributed message passing)
- MySQL-python >= 1.2.3 (MySQL for python language)
- Werkzeug >= 0.6.2 (Collection of various utilities for WSGI applications)
- amqplib >= 0.6.1 (Client library for AMQP)
- anyjson >= 0.3 (Loads the fastest JSON module)
- django-celery >= 3.1.1 (Celery integration for Django)
- django-extensions >= 1.0.3 (Collection of global custom management extensions for Django)
- django-jsonfield >= 0.9.12 (Reusable django field that can use inside models)
- django-pagination >= 1.0.7 (Utilities for creating robust pagination tools throughout a django application)
- django-picklefield >= 0.3.1 (Implementation of a pickled object field)
- django-threaded-multihost >= 1.4-0 (Provides multi-host utilities to Django projects)
- django-urlauth = 0.1.8 (Allows to build links with authentication effect )
- django-uuidfield >= 0.4 (Provides a UUIDField for your Django models)
- django-reusableapps >= 0.1.1 (Python module to enable Django to load reusable, pluggable and egg-based applications)
- docutils >= 0.10 (Text processing system for processing plaintext documentation into useful formats)
- importlib >= 1.0.2 (Implementation of the `import` statement)
- kombu >= 3.0.7 (An AMQP - Advanced Message Queuing Protocol messaging framework for Python)
- pyparsing >= 1.5.6 (A general parsing module for Python)
- python-dateutil >= 1.5 (Extensions to the standard datetime module)
- redis >= 2.8 (Redis Python Client)
- uuid >= 1.30 (UUID object and generation functions )
- wsgiref >= 0.1.2 (Validation support for WSGI )
- django-lets-go >= 2.8.5 (Common library that are reused by Star2Billing)
- django-country-dialcode >= 0.4.8 (Provide Prefix and Country information)
- djangorestframework == 2.3.9 (Creating delicious APIs for Django)
- BeautifulSoup >= 3.2.1 (HTML parser optimized for screen-scraping)
- Pygments >= 1.6 (A generic syntax highlighter)
- django-admin-tools (Collection of tools for the django administration)
- python-memcached >= 1.48 (Python based API for communicating with the memcached distributed memory object cache daemon)
- django-memcache-status >= 1.0.1 (Displays statistics about memcached instances)
- django-notification >= 0.2 (User notification management for the Django web framework)
- identicon (identicon python implementation)
- django-sentry >= 1.8.6.2 (Real-time logging / error tracing for Django)
- django-qsstats-magic >= 0.7.2 (A django microframework that eases the generation of aggregate data for querysets)
- django-frontend-notification >= 0.1.8 (Django application to display quickly on frontend the list of notification and run some basic actions such as view all notifications, delete notifications, etc...)


Use PIP to install all the requirements,::

    $ pip install -r requirements.txt


.. _installation-script:

Installation Script
===================

You can install Newfies-Dialer manually or using the shell script provided.

To install Newfies-Dialer using this script,::

    $ chmod +x install/install-newfies.sh

    $ ./install/install-newfies.sh


.. _running-newfies-dialer:

Running Newfies-Dialer
========================

Inside Newfies-Dialer directory you should run::

    $ python manage.py syncdb

    $ python manage.py collectstatic

    $ python manage.py runserver


``syncdb`` will create a database named test.db in ``database`` folder of the
Newfies-Dialer directory. We have configured Newfies-Dialer to do this, but you
can change this simply by modifying settings.py where DATABASES dictionary is
constructed. You can find more information about this in the
Django documentation.

``collectstatic`` will fetch all necessary media files and put them into
``static`` folder defined in the settings module.

``runserver`` runs an embedded webserver to test your site.
By default it will run on http://localhost:8000. This is configurable and more
information can be found on ``runserver`` in Django documentation.


.. _caching-system:

Caching System
==============

When a User requests a page, the Web server makes calculations
for business logic and to create the page that your visitor sees.
It creates a processing overhead higher than a standard
read-a-file-off-the-filesystem server arrangement.

This is where caching comes in.

To cache something is to save the result of an expensive calculation so that
you don’t have to perform the calculation next time::

    $ mkdir /usr/share/django_cache
