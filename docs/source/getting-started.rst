
.. _getting_started:

Getting Started
===============

:Web: http://www.newfies-dialer.org/
:Download: http://www.newfies-dialer.org/download/
:Source: https://github.com/Star2Billing/newfies-dialer/
:Keywords: dialer, voip, freeswitch, django, asynchronous, rabbitmq, redis, python, distributed


--

Newfies is an open source VoIP Dialer and SMS broadcasting system based on distributed message passing.
It has been built to support cloud based servers and can also work on standalone servers.
It uses `Freeswitch`_ (VoIP Server) to outbound calls.

The platform is focused on real-time operations and task call distributions
to clustered brokers and workers.

Newfies-Dialer is written in Python, using the `Django`_ Framework. It also operates
with message brokers such as `RabbitMQ`_, `Redis`_ but support for Beanstalk,
MongoDB, CouchDB and DBMS is also available.

Newfies-Dialer provides an extensive set of APIs to easily integrate with
third-party applications. Virtually every feature on the UI can be managed 
via the API's. There is also an API explorer to test different features.

Using very simple steps, Newfies-Dialer will help you create campaigns, add
phonebooks, contacts, build audio messages and create complex telephony
applications. Once the campaigns are ready to start, the messages
will be dispatched and delivered.

.. _`Freeswitch`: http://www.freeswitch.org/
.. _`Asterisk`: http://www.asterisk.org/
.. _`Django`: http://djangoproject.com/
.. _`RabbitMQ`: http://www.rabbitmq.com/
.. _`Redis`: http://code.google.com/p/redis/


.. contents::
    :local:
    :depth: 1


.. _overview:

Overview
--------

Newfies-Dialer can be installed and used by anyone who has a need for SMS broadcasting, 
mass outbound calling, voice broadcasting or providing outbound IVR Some of the
potential uses for Newfies-Dialer are listed below.

The system may be installed and used by either companies who wish to make calls
on their own behalf, or by SaaS (Software as a Service) companies that want to
provide bulk dialling and SMS broadcasting facilities to their own customers.

Newfies-Dialer can be configured on a single server, or for really high capacity 
or high speed systems, Newfies-Dialer can be configured across multiple servers.


.. _utility:

Utility
--------
Newfies-Dialer is loaded up with a list of telephone numbers that can be dialled
sequentially at very high rates of calling depending on carrier capacity and
hardware, potentially delivering many millions of calls per day.

When the called party answers the call, Newfies-Dialer passes the call to a telephony
application that is custom designed to provide the desired behaviour.

Some examples of where Newfies-Dialer may be used follow:


    * **Telecasting**: Broadcast marketing or informational messages to customers and clients.

    * **Phone Polling, Surveys and Voting**: Ring large numbers of people and present
      IVR options for either polling their opinions, interactive surveys, or taking
      their vote and record the results.

    * **Debt Control**: Customers can be automatically reminded at intervals that
      they owe money, and an IVR menu presented to talk to the finance department
      or passed to a credit card capture IVR to pay over the phone.

    * **Appointment Reminders**: Doctors, Dentists, and other organisations that make
      appointments for their clients can integrate Newfies-Dialer into their
      appointment systems to pass a message reminding clients of an upcoming appointment.

    * **Dissemination of information via phone**: Newfies-Dialer was originally
      designed to call large numbers of people and disseminate medical and health advice
      via cellphone in 3rd world countries where often, literacy levels are low. On a 
      local scale, it can be used to disseminate information about forthcoming community events.

    * **Mass Emergency broadcast**: Where there is a necessity to warn large numbers
      of people in a short space of time, such as weather warnings, evacuation notices
      and crime prevention.

    * **Subscription Reminders and Renewals**: Where a company sells an annual
      subscription for a product or service, Newfies-Dialer can be configured to
      dial the customer, remind them that the subscription is due.


.. _features:

Features
--------

    +-----------------+----------------------------------------------------+
    | Broadcasting    | Web-based SMS and Voice Broadcasting application.  |
    +-----------------+----------------------------------------------------+
    | Distributed     | Runs on one or more machines. Supports             |
    |                 | broker `clustering` and `HA` when used in          |
    |                 | combination with `RabbitMQ`.  You can set up new   |
    |                 | workers without central configuration.             |
    +-----------------+----------------------------------------------------+
    | Concurrency     | Throttle Concurrent Calls.                         |
    +-----------------+----------------------------------------------------+
    | Scheduling      | Supports recurring tasks like cron, or specifying  |
    |                 | an exact date or countdown for when the task       |
    |                 | should be executed. Can re-try failed calls at a   |
    |                 | later time.                                        |
    +-----------------+----------------------------------------------------+
    | IVR support     | Accommodates multiple IVR scripts with options to  |
    |                 | connect the user to another IVR/phone number on    |
    |                 | pressing a key.                                    |
    +-----------------+----------------------------------------------------+
    | Web Interface   | Newfies-Dialer can be managed via a Web interface. |
    |                 | Realtime web-based reports for call details and    |
    |                 | current calls.                                     |
    +-----------------+----------------------------------------------------+
    | Import Contact  | Import contact details from a .csv file            |
    +-----------------+----------------------------------------------------+
    | Multi-tenant    | It provies different roles for end-users, staff    |
    |                 | and administrators. With Appointment reminders     |
    |                 | module, it also provides Calendar Users.           |
    +-----------------+----------------------------------------------------+
    | RealTime Control| Control the speed of campaigns in realtime, as well|
    |                 | as start, stop and pause buttons to control the    |
    |                 | campaigns                                          |
    +-----------------+----------------------------------------------------+
    | Surveys         | IVR designer application enable the easy creation  |
    |                 | of survey application used. Survey reports can be  |
    |                 | consulted in real-time.                            |
    +-----------------+----------------------------------------------------+
    | Audio file      | Support multiple audio file formats : wav, mp3,    |
    |                 | ogg, gsm, etc...                                   |
    +-----------------+----------------------------------------------------+
    | Text2Speech     | Supports powerful text2speech engines : Flite,     |
    |                 | Acapela & Cepstral. Acapela covers a wide range    |
    |                 | languages.                                         |
    +-----------------+----------------------------------------------------+
    | DNC             | Support Do Not Call List. Several DNC lists can be |
    |                 | managed per campaign and per user.                 |
    +-----------------+----------------------------------------------------+
    | SMS             | SMS delivery, SMS Gateway support, SMS campaign.   |
    |                 |                                                    |
    +-----------------+----------------------------------------------------+


.. _extra_features:

Extra Features
--------------

    +----------------+------------------------------------------------------+
    | AMD            | Answering Machine Detection module is available.     |
    |                | For this module see the section Add-ons on website   |
    +----------------+------------------------------------------------------+
    | Rebranding &   | Rebranding and design services to match your         |
    | Whitelabelling | corporate imagee. See the Add-ons section on website |
    +----------------+------------------------------------------------------+


.. _architecture:

Architecture
------------

.. image:: ./_static/images/newfies-dialer_architecture.png

* User selects contacts, phonebooks and campaigns, then chooses a voice application to use. The campaign is then launched

* **Newfies-Dialer** spools the outbound calls to **FreeSWITCH** via **ESL**.

* **FreeSWITCH** dials the contact via the configured telephony gateways.

* Contact picks up the call, and the answer event is received in **FreeSWITCH** and passed back to the Lua IVR Application.

* **Newfies-Dialer** is notified that the call is answered, then renders the appropriate IVR.

* The application is delivered to the contact by **FreeSWITCH**.
