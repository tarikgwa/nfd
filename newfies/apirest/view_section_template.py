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
from apirest.section_template_serializers import SectionTemplateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from survey.models import Section_template
from apirest.permissions import CustomObjectPermissions


class SectionTemplateViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows content_type to be viewed or edited.
    """
    model = Section_template
    queryset = Section_template.objects.all()
    serializer_class = SectionTemplateSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the sections
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Section_template.objects.all()
        else:
            queryset = Section_template.objects.filter(survey__user=self.request.user)
        return queryset
