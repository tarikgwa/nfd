# -*- coding: utf-8 -*-

#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):

    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/users/

        Response::

            {
                "count": 3,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/users/3/",
                        "username": "agent",
                        "last_name": "",
                        "first_name": "",
                        "email": "",
                        "groups": []
                    },
                    {
                        "url": "http://127.0.0.1:8000/rest-api/users/2/",
                        "username": "manager",
                        "last_name": "",
                        "first_name": "",
                        "email": "",
                        "groups": []
                    },
                    {
                        "url": "http://127.0.0.1:8000/rest-api/users/1/",
                        "username": "root",
                        "last_name": "",
                        "first_name": "",
                        "email": "root@gmail.com",
                        "groups": []
                    }
                ]
            }
    """

    class Meta:
        model = User
        fields = ('url', 'username', 'last_name', 'first_name', 'email', 'groups')
