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

from django.utils.translation import ugettext_lazy as _
from django_lets_go.utils import Choice


class CALLREQUEST_STATUS(Choice):

    """
    Store the Call Request Status
    """
    PENDING = 1, _("pending")
    FAILURE = 2, _("failure")
    RETRY = 3, _("retry")
    SUCCESS = 4, _("success")
    ABORT = 5, _("abort")
    PAUSE = 6, _("pause")
    CALLING = 7, _("calling")


class CALLREQUEST_TYPE(Choice):

    """
    Store the Call Request Type
    """
    ALLOW_RETRY = 1, _('ALLOW RETRY')
    CANNOT_RETRY = 2, _('CANNOT RETRY')
    RETRY_DONE = 3, _('RETRY DONE')


class LEG_TYPE(Choice):

    """
    Store the Leg Type
    """
    A_LEG = 1, _('A-Leg')
    B_LEG = 2, _('B-Leg')


class CALL_DISPOSITION(Choice):

    """
    Store the Call Disposition
    """
    ANSWER = 'ANSWER', _('ANSWER')
    BUSY = 'BUSY', _('BUSY')
    NOANSWER = 'NOANSWER', _('NOANSWER')
    CANCEL = 'CANCEL', _('CANCEL')
    CONGESTION = 'CONGESTION', _('CONGESTION')
    FAILED = 'FAILED', _('FAILED')  # Added to catch all


# Column Name for the CDR Report
CDR_REPORT_COLUMN_NAME = {
    'date': _('start date'),
    'call_id': _('call ID'),
    'leg': _('leg'),
    'caller_id': _('caller ID'),
    'phone_no': _('phone no'),
    'gateway': _('gateway'),
    'duration': _('duration'),
    'bill_sec': _('bill sec'),
    'disposition': _('disposition'),
    'amd_status': _('amd status')
}


class VOIPCALL_AMD_STATUS(Choice):

    """
    Store the AMD Status
    """
    PERSON = 1, _("PERSON")
    MACHINE = 2, _("MACHINE")
    UNSURE = 3, _("UNSURE")
