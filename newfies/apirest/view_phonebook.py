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

from rest_framework import viewsets
from apirest.phonebook_serializers import PhonebookSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_contact.models import Phonebook
from apirest.permissions import CustomObjectPermissions


class PhonebookViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows phonebook to be viewed or edited.
    """
    model = Phonebook
    queryset = Phonebook.objects.all()
    serializer_class = PhonebookSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the phonebooks
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Phonebook.objects.all()
        else:
            queryset = Phonebook.objects.filter(user=self.request.user)
        return queryset

    def pre_save(self, obj):
        obj.user = self.request.user
