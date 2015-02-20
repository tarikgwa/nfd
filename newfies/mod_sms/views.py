#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from dialer_contact.models import Contact
from dialer_contact.constants import CONTACT_STATUS
from dialer_campaign.function_def import date_range, user_dialer_setting, \
    dialer_setting_limit
from frontend.function_def import calculate_date
from frontend.constants import SEARCH_TYPE
from frontend_notification.views import frontend_send_notification
from django_lets_go.common_functions import get_pagination_vars, ceil_strdate,\
    percentage, getvar, unset_session_var
from mod_utils.helper import Export_choice
from mod_sms.models import SMSCampaign, SMSCampaignSubscriber, SMSMessage
from mod_sms.constants import SMS_CAMPAIGN_STATUS, SMS_CAMPAIGN_COLUMN_NAME,\
    SMS_REPORT_COLUMN_NAME, COLOR_SMS_DISPOSITION, SMS_NOTIFICATION_NAME,\
    SMS_SUBSCRIBER_STATUS, SMS_MESSAGE_STATUS
from mod_sms.forms import SMSCampaignForm, SMSDashboardForm, SMSSearchForm,\
    SMSCampaignSearchForm, DuplicateSMSCampaignForm
from mod_sms.function_def import check_sms_dialer_setting, get_sms_notification_status
from datetime import datetime
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta
import tablib
import time


redirect_url_to_smscampaign_list = '/sms_campaign/'


@login_required
def update_sms_campaign_status_admin(request, pk, status):
    """SMS Campaign Status (e.g. start|stop|pause|abort) can be changed from
    admin interface (via sms campaign list)"""
    smscampaign = SMSCampaign.objects.get(pk=pk)
    recipient = smscampaign.common_sms_campaign_status(status)
    sms_notification_status = get_sms_notification_status(int(status))
    frontend_send_notification(request, sms_notification_status, recipient)
    return HttpResponseRedirect(reverse("admin:mod_sms_smscampaign_changelist"))


@login_required
def update_sms_campaign_status_cust(request, pk, status):
    """SMS Campaign Status (e.g. start|stop|pause|abort) can be changed from
    customer interface (via sms campaign list)"""
    smscampaign = SMSCampaign.objects.get(pk=pk)
    recipient = smscampaign.common_sms_campaign_status(status)
    sms_notification_status = get_sms_notification_status(int(status))
    frontend_send_notification(request, sms_notification_status, recipient)
    return HttpResponseRedirect(redirect_url_to_smscampaign_list)


# SMSCampaign
@permission_required('mod_sms.view_smscampaign', login_url='/')
@login_required
def sms_campaign_list(request):
    """List all sms campaigns for the logged in user

    **Attributes**:

        * ``template`` - mod_sms/list.html

    **Logic Description**:

        * List all sms campaigns belonging to the logged in user
    """
    form = SMSCampaignSearchForm(request.user, request.POST or None)
    sort_col_field_list = ['id', 'name', 'startingdate', 'status', 'totalcontact']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')

    phonebook_id = ''
    status = 'all'
    post_var_with_page = 0
    if form.is_valid():
        field_list = ['phonebook_id', 'status']
        unset_session_var(request, field_list)
        post_var_with_page = 1
        phonebook_id = getvar(request, 'phonebook_id', setsession=True)
        status = getvar(request, 'status', setsession=True)

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        phonebook_id = request.session.get('session_phonebook_id')
        status = request.session.get('session_status')
        form = SMSCampaignSearchForm(request.user, initial={'status': status,
                                                            'phonebook_id': phonebook_id})

    if post_var_with_page == 0:
        # default
        # unset session var
        field_list = ['status', 'phonebook_id']
        unset_session_var(request, field_list)

    kwargs = {}
    if phonebook_id and phonebook_id != '0':
        kwargs['phonebook__id__in'] = [int(phonebook_id)]

    if status and status != 'all':
        kwargs['status'] = status

    smscampaign_list = SMSCampaign.objects.filter(user=request.user).order_by(pag_vars['sort_order'])
    smscampaign_count = smscampaign_list.count()
    if kwargs:
        all_smscampaign_list = smscampaign_list.filter(**kwargs).order_by(pag_vars['sort_order'])
        smscampaign_list = all_smscampaign_list[pag_vars['start_page']:pag_vars['end_page']]
        smscampaign_count = all_smscampaign_list.count()

    data = {
        'form': form,
        'smscampaign_list': smscampaign_list,
        'total_campaign': smscampaign_count,
        'SMS_CAMPAIGN_COLUMN_NAME': SMS_CAMPAIGN_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'info_msg': request.session.get('info_msg'),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    request.session['info_msg'] = ''
    return render_to_response('mod_sms/list.html', data, context_instance=RequestContext(request))


@permission_required('mod_sms.add_smscampaign', login_url='/')
@login_required
def sms_campaign_add(request):
    """Add a new sms campaign for the logged in user

    **Attributes**:

        * ``form`` - SMSCampaignForm
        * ``template`` - mod_sms/change.html

    **Logic Description**:

        * Before adding a sms campaign, check dialer setting limit if
          applicable to the user.
        * Add the new sms campaign which will belong to the logged in user
          via SMSCampaignForm & get redirected to sms campaign list
    """
    # If dialer setting is not attached with user, redirect to sms campaign list
    if not user_dialer_setting(request.user):
        request.session['error_msg'] = \
            _("in order to add a sms campaign, you need to have your \
               settings configured properly, please contact the admin.")
        return HttpResponseRedirect(redirect_url_to_smscampaign_list)

    # Check dialer setting limit
    if request.user and request.method != 'POST':
        # check Max Number of running campaign
        if check_sms_dialer_setting(request, check_for="smscampaign"):
            msg = _("you have too many sms campaigns. Max allowed %(limit)s")\
                % {'limit': dialer_setting_limit(request, limit_for="smscampaign")}
            request.session['msg'] = msg

            # sms campaign limit reached
            frontend_send_notification(request, SMS_NOTIFICATION_NAME.sms_campaign_limit_reached)
            return HttpResponseRedirect(redirect_url_to_smscampaign_list)

    form = SMSCampaignForm(request.user, request.POST or None)
    # Add sms campaign
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = User.objects.get(username=request.user)
        obj.stoppeddate = obj.expirationdate
        obj.save()
        form.save_m2m()
        request.session["msg"] = _('"%(name)s" is added.') % {'name': request.POST['name']}
        return HttpResponseRedirect(redirect_url_to_smscampaign_list)

    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('mod_sms/change.html', data, context_instance=RequestContext(request))


@permission_required('mod_sms.delete_smsmessage', login_url='/')
@login_required
def sms_campaign_del(request, object_id):
    """Delete/Stop sms campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected sms campaign object
        * ``object_list`` - Selected sms campaign objects

    **Logic Description**:

        * Delete/Stop the selected sms campaign from the sms campaign list
    """
    stop_sms_campaign = request.GET.get('stop_sms_campaign', False)
    try:
        # When object_id is not 0
        sms_campaign = get_object_or_404(SMSCampaign, pk=object_id, user=request.user)
        # Delete/Stop sms campaign
        if sms_campaign:
            if stop_sms_campaign:
                sms_campaign.status = SMS_CAMPAIGN_STATUS.END
                sms_campaign.save()
                request.session["msg"] = _('"%(name)s" is stopped.') % {'name': sms_campaign.name}
            else:
                request.session["msg"] = _('"%(name)s" is deleted.') % {'name': sms_campaign.name}
                sms_campaign.delete()
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        sms_campaign_list = SMSCampaign.objects.extra(where=['id IN (%s)' % values])
        if sms_campaign_list:
            if stop_sms_campaign:
                sms_campaign_list.update(status=SMS_CAMPAIGN_STATUS.END)
                request.session["msg"] = _('%(count)s sms campaign(s) are stopped.') % {'count': sms_campaign_list.count()}
            else:
                request.session["msg"] = _('%(count)s sms campaign(s) are deleted.') % {'count': sms_campaign_list.count()}
                sms_campaign_list.delete()
    return HttpResponseRedirect(redirect_url_to_smscampaign_list)


@permission_required('mod_sms.change_smsmessage', login_url='/')
@login_required
def sms_campaign_change(request, object_id):
    """Update/Delete sms campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``form`` - SMSCampaignForm
        * ``template`` - mod_sms/change.html

    **Logic Description**:

        * Update/delete selected sms campaign from the sms campaign list
          via SMSCampaignForm & get redirected to the sms campaign list
    """
    # If dialer setting is not attached with user, redirect to sms campaign list
    if not user_dialer_setting(request.user):
        return HttpResponseRedirect(redirect_url_to_smscampaign_list)

    sms_campaign = get_object_or_404(SMSCampaign, pk=object_id, user=request.user)
    form = SMSCampaignForm(request.user, request.POST or None, instance=sms_campaign)
    if form.is_valid():
        # Delete sms campaign
        if request.POST.get('delete'):
            sms_campaign_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_smscampaign_list)
        else:
            # Update sms campaign
            obj = form.save()
            obj.save()
            request.session["msg"] = _('"%(name)s" is updated.') % {'name': request.POST['name']}
            return HttpResponseRedirect(redirect_url_to_smscampaign_list)
    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('mod_sms/change.html', data, context_instance=RequestContext(request))


@login_required
def sms_campaign_duplicate(request, id):
    """
    Duplicate sms campaign via DuplicateSMSCampaignForm

    **Attributes**:

        * ``id`` - Selected sms campaign object
        * ``form`` - DuplicateSMSCampaignForm
        * ``template`` - mod_sms/sms_campaign_duplicate.html
    """
    # If dialer setting is not attached with user, redirect to sms campaign list
    if not user_dialer_setting(request.user):
        return HttpResponseRedirect(redirect_url_to_smscampaign_list)

    form = DuplicateSMSCampaignForm(request.user, request.POST or None)
    request.session['error_msg'] = ''
    if request.method == 'POST':
        if form.is_valid():
            sms_campaign_obj = SMSCampaign.objects.get(pk=id)

            sms_campaign_obj.pk = None
            sms_campaign_obj.campaign_code = request.POST.get('campaign_code')
            sms_campaign_obj.name = request.POST.get('name')
            sms_campaign_obj.status = SMS_CAMPAIGN_STATUS.PAUSE
            sms_campaign_obj.startingdate = datetime.utcnow().replace(tzinfo=utc)
            sms_campaign_obj.expirationdate = datetime.utcnow().replace(tzinfo=utc) + relativedelta(days=+1)
            sms_campaign_obj.stoppeddate = datetime.utcnow().replace(tzinfo=utc) + relativedelta(days=+1)
            sms_campaign_obj.imported_phonebook = ''
            sms_campaign_obj.totalcontact = 0
            sms_campaign_obj.save()

            # Many to many field
            for pb in request.POST.getlist('phonebook'):
                sms_campaign_obj.phonebook.add(pb)

            return HttpResponseRedirect(redirect_url_to_smscampaign_list)
        else:
            request.session['error_msg'] = True

    data = {
        'sms_campaign_id': id,
        'form': form,
        'err_msg': request.session.get('error_msg'),
    }
    request.session['error_msg'] = ''
    return render_to_response('mod_sms/sms_campaign_duplicate.html', data, context_instance=RequestContext(request))


@login_required
def sms_campaign_text_message(request, object_id):
    """
    Get sms campaign's text message

    **Attributes**:

        * ``object_id`` - Selected sms campaign object
        * ``template`` - mod_sms/sms_campaign_text_message.html
    """
    # If dialer setting is not attached with user, redirect to sms campaign list
    if not user_dialer_setting(request.user):
        return HttpResponseRedirect(redirect_url_to_smscampaign_list)

    sms_campaign = get_object_or_404(SMSCampaign, pk=object_id, user=request.user)
    data = {
        'sms_campaign': sms_campaign,
    }
    request.session['error_msg'] = ''
    return render_to_response('mod_sms/sms_campaign_text_message.html', data, context_instance=RequestContext(request))


@permission_required('mod_sms.view_sms_dashboard', login_url='/')
@login_required
def sms_dashboard(request, on_index=None):
    """SMS dashboard gives the following information

        * No of SMSCampaigns for logged in user
        * Total phonebook contacts
        * Total SMSCampaigns contacts
        * Amount of contact reached today
        * Disposition of sms via pie chart
        * SMS count shown on graph by days/hours

    **Attributes**:

        * ``template`` - mod_sms/sms_dashboard.html
        * ``form`` - SMSDashboardForm
    """
    # All sms_campaign for logged in User
    sms_campaign_id_list = SMSCampaign.objects.values_list('id', flat=True).filter(user=request.user).order_by('id')

    # Contacts count which are active and belong to those phonebook(s) which is
    # associated with all sms campaign
    pb_active_contact_count = Contact.objects.filter(
        phonebook__smscampaign__in=sms_campaign_id_list,
        status=CONTACT_STATUS.ACTIVE).count()

    form = SMSDashboardForm(request.user, request.POST or None)

    total_record = dict()
    total_sms_count = 0
    total_unsent = 0
    total_sent = 0
    total_delivered = 0
    total_failed = 0
    total_no_route = 0
    total_unauthorized = 0

    select_graph_for = 'sms count'  # default
    search_type = SEARCH_TYPE.D_Last_24_hours  # default Last 24 hours
    selected_sms_campaign = ''

    if sms_campaign_id_list:
        selected_sms_campaign = sms_campaign_id_list[0]  # default sms campaign id

    # selected_sms_campaign should not be empty
    if selected_sms_campaign:

        if form.is_valid():
            selected_sms_campaign = request.POST['smscampaign']
            search_type = request.POST['search_type']

        end_date = datetime.utcnow().replace(tzinfo=utc)
        start_date = calculate_date(search_type)

        # date_length is used to do group by starting_date
        if int(search_type) >= SEARCH_TYPE.B_Last_7_days:  # all options except 30 days
            date_length = 13
            if int(search_type) == SEARCH_TYPE.C_Yesterday:  # yesterday
                now = datetime.utcnow().replace(tzinfo=utc)
                start_date = datetime(now.year, now.month, now.day, 0, 0, 0, 0).replace(tzinfo=utc) \
                    - relativedelta(days=1)
                end_date = datetime(now.year, now.month, now.day, 23, 59, 59, 999999).replace(tzinfo=utc) \
                    - relativedelta(days=1)
            if int(search_type) >= SEARCH_TYPE.E_Last_12_hours:
                date_length = 16
        else:
            date_length = 10  # Last 30 days option

        select_data = {
            "send_date": "SUBSTR(CAST(send_date as CHAR(30)),1," + str(date_length) + ")"}

        # This calls list is used by pie chart
        list_sms = SMSMessage.objects.filter(
            sender=request.user,
            sms_campaign_id=selected_sms_campaign,
            send_date__range=(start_date, end_date))\
            .extra(select=select_data)\
            .values('send_date', 'status')\
            .annotate(Count('send_date'))\
            .order_by('send_date')

        for i in list_sms:
            # convert unicode date string into date
            if i['status'] == 'Unsent':
                total_unsent += i['send_date__count']
            elif i['status'] == 'Sent':
                total_sent += i['send_date__count']
            elif i['status'] == 'Delivered':
                total_delivered += i['send_date__count']
            elif i['status'] == 'Failed':
                total_failed += i['send_date__count']
            elif i['status'] == 'No_Route':
                total_no_route += i['send_date__count']
            else:
                total_unauthorized += i['send_date__count']  # Unauthorized

            total_sms_count += i['send_date__count']

        list_sms = SMSMessage.objects.filter(
            sender=request.user,
            sms_campaign_id=selected_sms_campaign,
            send_date__range=(start_date, end_date))\
            .extra(select=select_data).values('send_date')\
            .annotate(Count('send_date')).order_by('send_date')

        mintime = start_date
        maxtime = end_date
        sms_dict = {}
        sms_dict_with_min = {}

        for data in list_sms:
            if int(search_type) >= SEARCH_TYPE.B_Last_7_days:
                ctime = datetime(int(data['send_date'][0:4]),
                                 int(data['send_date'][5:7]),
                                 int(data['send_date'][8:10]),
                                 int(data['send_date'][11:13]),
                                 0, 0, 0).replace(tzinfo=utc)
                if int(search_type) >= SEARCH_TYPE.E_Last_12_hours:
                    ctime = datetime(int(data['send_date'][0:4]),
                                     int(data['send_date'][5:7]),
                                     int(data['send_date'][8:10]),
                                     int(data['send_date'][11:13]),
                                     int(data['send_date'][14:16]),
                                     0, 0).replace(tzinfo=utc)
            else:
                ctime = datetime(int(data['send_date'][0:4]),
                                 int(data['send_date'][5:7]),
                                 int(data['send_date'][8:10]),
                                 0, 0, 0, 0).replace(tzinfo=utc)
            if ctime > maxtime:
                maxtime = ctime
            elif ctime < mintime:
                mintime = ctime

            # all options except 30 days
            if int(search_type) >= SEARCH_TYPE.B_Last_7_days:
                sms_dict[int(ctime.strftime("%Y%m%d%H"))] = {
                    'sms_count': data['send_date__count']
                }
                sms_dict_with_min[int(ctime.strftime("%Y%m%d%H%M"))] = {
                    'sms_count': data['send_date__count']
                }
            else:
                # Last 30 days option
                sms_dict[int(ctime.strftime("%Y%m%d"))] = {
                    'sms_count': data['send_date__count']
                }

        dateList = date_range(mintime, maxtime, q=search_type)

        i = 0
        total_record = {}
        for date in dateList:
            inttime = int(date.strftime("%Y%m%d"))
            # last 7 days | yesterday | last 24 hrs
            if (int(search_type) == SEARCH_TYPE.B_Last_7_days
                    or int(search_type) == SEARCH_TYPE.C_Yesterday
                    or int(search_type) == SEARCH_TYPE.D_Last_24_hours):

                for option in range(0, 24):
                    day_time = int(str(inttime) + str(option).zfill(2))

                    graph_day = datetime(int(date.strftime("%Y")),
                                         int(date.strftime("%m")),
                                         int(date.strftime("%d")),
                                         int(str(option).zfill(2))).replace(tzinfo=utc)

                    dt = int(1000 * time.mktime(graph_day.timetuple()))
                    total_record[dt] = {'sms_count': 0}

                    if day_time in sms_dict.keys():
                        total_record[dt]['sms_count'] += sms_dict[day_time]['sms_count']

            # last 12 hrs | last 6 hrs | last 1 hrs
            elif (int(search_type) == SEARCH_TYPE.E_Last_12_hours
                  or int(search_type) == SEARCH_TYPE.F_Last_6_hours
                  or int(search_type) == SEARCH_TYPE.G_Last_hour):

                for hour in range(0, 24):
                    for minute in range(0, 60):
                        hr_time = int(str(inttime) + str(hour).zfill(2) + str(minute).zfill(2))

                        graph_day = datetime(int(date.strftime("%Y")),
                                             int(date.strftime("%m")),
                                             int(date.strftime("%d")),
                                             int(str(hour).zfill(2)),
                                             int(str(minute).zfill(2))).replace(tzinfo=utc)

                        dt = int(1000 * time.mktime(graph_day.timetuple()))
                        total_record[dt] = {'sms_count': 0}

                        if hr_time in sms_dict_with_min.keys():
                            total_record[dt]['sms_count'] += sms_dict_with_min[hr_time]['sms_count']

            else:
                # Last 30 days option
                graph_day = datetime(int(date.strftime("%Y")),
                                     int(date.strftime("%m")),
                                     int(date.strftime("%d"))).replace(tzinfo=utc)
                dt = int(1000 * time.mktime(graph_day.timetuple()))
                total_record[dt] = {'sms_count': 0}
                if inttime in sms_dict.keys():
                    total_record[dt]['sms_count'] += sms_dict[inttime]['sms_count']

    # sorting on date col
    total_record = total_record.items()
    total_record = sorted(total_record, key=lambda k: k[0])

    # lineWithFocusChart
    final_charttype = "lineWithFocusChart"
    xdata = []
    ydata = []
    for i in total_record:
        xdata.append(i[0])
        ydata.append(i[1]['sms_count'])

    tooltip_date = "%d %b %y %H:%M %p"
    extra_serie1 = {
        "tooltip": {"y_start": "", "y_end": " SMS"},
        "date_format": tooltip_date
    }

    final_chartdata = {
        'x': xdata,
        'name1': 'SMS', 'y1': ydata, 'extra1': extra_serie1,
    }

    # Contacts which are successfully messaged for running sms campaign
    reached_contact = 0
    if sms_campaign_id_list:
        now = datetime.utcnow().replace(tzinfo=utc)
        start_date = datetime(now.year, now.month, now.day, 0, 0, 0, 0).replace(tzinfo=utc)
        end_date = datetime(now.year, now.month, now.day, 23, 59, 59, 999999).replace(tzinfo=utc)
        sms_campaign_subscriber = SMSCampaignSubscriber.objects.filter(
            sms_campaign_id__in=sms_campaign_id_list,
            status=SMS_SUBSCRIBER_STATUS.COMPLETE,
            updated_date__range=(start_date, end_date)).count()
        reached_contact += sms_campaign_subscriber

    # PieChart
    sms_analytic_charttype = "pieChart"
    xdata = []
    ydata = []
    sms_analytic_chartdata = {'x': xdata, 'y1': ydata}

    if total_sms_count != 0:
        for i in SMS_MESSAGE_STATUS:
            xdata.append(i[0].upper())

        # Y-axis order depend upon SMS_MESSAGE_STATUS
        # 'UNSENT', 'SENT', 'DELIVERED', 'FAILED', 'NO_ROUTE', 'UNAUTHORIZED'
        ydata = [
            percentage(total_unsent, total_sms_count),
            percentage(total_sent, total_sms_count),
            percentage(total_delivered, total_sms_count),
            percentage(total_failed, total_sms_count),
            percentage(total_no_route, total_sms_count),
            percentage(total_unauthorized, total_sms_count),
        ]

        color_list = [
            COLOR_SMS_DISPOSITION['UNSENT'],
            COLOR_SMS_DISPOSITION['SENT'],
            COLOR_SMS_DISPOSITION['DELIVERED'],
            COLOR_SMS_DISPOSITION['FAILED'],
            COLOR_SMS_DISPOSITION['NO_ROUTE'],
            COLOR_SMS_DISPOSITION['UNAUTHORIZED'],
        ]
        extra_serie = {
            "tooltip": {"y_start": "", "y_end": " %"},
            "color_list": color_list
        }
        kwargs1 = {}
        kwargs1['resize'] = True
        sms_analytic_chartdata = {
            'x': xdata, 'y1': ydata, 'extra1': extra_serie,
            'kwargs1': kwargs1,
        }

    data = {
        'form': form,
        'SEARCH_TYPE': SEARCH_TYPE,
        'pb_active_contact_count': pb_active_contact_count,
        'reached_contact': reached_contact,
        'total_record': total_record,
        'select_graph_for': select_graph_for,
        'total_sms_count': total_sms_count,
        'total_unsent': total_unsent,
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_failed': total_failed,
        'total_no_route': total_no_route,
        'total_unauthorized': total_unauthorized,
        'unsent_color': COLOR_SMS_DISPOSITION['UNSENT'],
        'sent_color': COLOR_SMS_DISPOSITION['SENT'],
        'delivered_color': COLOR_SMS_DISPOSITION['DELIVERED'],
        'failed_color': COLOR_SMS_DISPOSITION['FAILED'],
        'no_route_color': COLOR_SMS_DISPOSITION['NO_ROUTE'],
        'unauthorized_color': COLOR_SMS_DISPOSITION['UNAUTHORIZED'],
        'final_chartcontainer': 'lineplusbarwithfocuschart_container',
        'final_chartdata': final_chartdata,
        'final_charttype': final_charttype,
        'final_extra': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y',
            'tag_script_js': True,
            'jquery_on_ready': False,
        },
        'sms_analytic_chartcontainer': 'piechart_container',
        'sms_analytic_charttype': sms_analytic_charttype,
        'sms_analytic_chartdata': sms_analytic_chartdata,
        'sms_analytic_extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        },
    }
    if on_index == 'yes':
        return data
    return render_to_response('mod_sms/sms_dashboard.html', data, context_instance=RequestContext(request))


@login_required
@permission_required('mod_sms.view_sms_report', login_url='/')
def sms_report(request):
    """SMS Report

    **Attributes**:

        * ``form`` - SMSSearchForm
        * ``template`` - mod_sms/sms_report.html

    **Logic Description**:

        * Get SMS list according to search parameters for logged-in user

    **Important variable**:

        * ``request.session['sms_record_kwargs']`` - stores sms kwargs
    """
    sort_col_field_list = ['send_date', 'recipient_number', 'uuid', 'status', 'status_message', 'gateway']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='send_date')

    from_date = ''
    to_date = ''
    status = 'all'
    smscampaign = ''

    form = SMSSearchForm(request.user, request.POST or None)
    action = 'tabs-1'
    kwargs = {}
    post_var_with_page = 0
    if form.is_valid():
        post_var_with_page = 1
        field_list = ['start_date', 'end_date', 'status', 'smscampaign']
        unset_session_var(request, field_list)

        from_date = getvar(request, 'from_date')
        to_date = getvar(request, 'to_date')
        start_date = ceil_strdate(str(from_date), 'start')
        end_date = ceil_strdate(str(to_date), 'end')

        converted_start_date = start_date.strftime('%Y-%m-%d')
        converted_end_date = end_date.strftime('%Y-%m-%d')
        request.session['session_start_date'] = converted_start_date
        request.session['session_end_date'] = converted_end_date

        status = getvar(request, 'status', setsession=True)
        smscampaign = getvar(request, 'smscampaign', setsession=True)

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        start_date = request.session.get('session_start_date')
        end_date = request.session.get('session_end_date')
        start_date = ceil_strdate(start_date, 'start')
        end_date = ceil_strdate(end_date, 'end')
        status = request.session.get('session_status')
        smscampaign = request.session.get('session_smscampaign')

        form = SMSSearchForm(request.user,
                             initial={'from_date': start_date.strftime('%Y-%m-%d'),
                                      'to_date': end_date.strftime('%Y-%m-%d'),
                                      'status': status,
                                      'smscampaign': smscampaign})

    if post_var_with_page == 0:
        # default
        tday = datetime.utcnow().replace(tzinfo=utc)
        from_date = tday.strftime('%Y-%m-%d')
        to_date = tday.strftime('%Y-%m-%d')
        start_date = datetime(tday.year, tday.month, tday.day, 0, 0, 0, 0).replace(tzinfo=utc)
        end_date = datetime(tday.year, tday.month, tday.day, 23, 59, 59, 999999).replace(tzinfo=utc)
        status = 'all'
        smscampaign = ''
        form = SMSSearchForm(request.user, initial={'from_date': from_date, 'to_date': to_date,
                                                    'status': status, 'smscampaign': smscampaign})
        # unset session var
        request.session['session_start_date'] = start_date
        request.session['session_end_date'] = end_date
        request.session['session_status'] = status
        request.session['session_smscampaign'] = smscampaign

    kwargs['sender'] = request.user

    if start_date and end_date:
        kwargs['send_date__range'] = (start_date, end_date)
    if start_date and end_date == '':
        kwargs['send_date__gte'] = start_date
    if start_date == '' and end_date:
        kwargs['send_date__lte'] = end_date

    if status and status != 'all':
        kwargs['status__exact'] = status

    if smscampaign and smscampaign != '0':
        kwargs['sms_campaign_id'] = smscampaign

    smslist = SMSMessage.objects.filter(**kwargs)
    all_sms_list = smslist.values_list('id', flat=True)
    sms_list = smslist.order_by(pag_vars['sort_order'])[pag_vars['start_page']:pag_vars['end_page']]

    # Session variable is used to get record set with searched option
    # into export file
    request.session['sms_record_kwargs'] = kwargs

    select_data = {"send_date": "SUBSTR(CAST(send_date as CHAR(30)),1,10)"}
    # Get Total Rrecords from SMSMessage Report table for Daily SMS Report
    total_data = all_sms_list.extra(select=select_data).values('send_date')\
        .annotate(Count('send_date')).order_by('-send_date')

    # Following code will count total sms
    if total_data.count() != 0:
        total_sms = sum([x['send_date__count'] for x in total_data])
    else:
        total_sms = 0

    data = {
        'form': form,
        'from_date': from_date,
        'all_sms_list': all_sms_list,
        'sms_list': sms_list,
        'sms_count': all_sms_list.count() if all_sms_list else 0,
        'SMS_REPORT_COLUMN_NAME': SMS_REPORT_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'start_date': start_date,
        'end_date': end_date,
        'to_date': to_date,
        'action': action,
        'status': status,
        'total_data': total_data.reverse(),
        'total_sms': total_sms,
    }

    return render_to_response('mod_sms/sms_report.html', data, context_instance=RequestContext(request))


@login_required
def export_sms_report(request):
    """Export CSV file of SMS record

    **Important variable**:

        * ``request.session['sms_record_kwargs']`` - stores sms query set

    **Exported fields**: ['sender', 'recipient_number', 'send_date', 'uuid',
               'status', 'status_message', 'gateway']
    """
    format_type = request.GET['format']
    # get the response object, this can be used as a stream.
    response = HttpResponse(content_type='text/%s' % format_type)

    # force download.
    response['Content-Disposition'] = 'attachment;filename=sms_export.%s' % format_type
    kwargs = {}
    kwargs = request.session['sms_record_kwargs']
    qs = SMSMessage.objects.filter(**kwargs)

    headers = ('sender', 'recipient_number', 'send_date', 'uuid',
               'status', 'status_message', 'gateway')
    list_val = []
    for i in qs:
        send_date = i.send_date
        if format_type == Export_choice.JSON or format_type == Export_choice.XLS:
            send_date = str(i.send_date)
        gateway = i.gateway.name if i.gateway else ''
        list_val.append([
            i.sender.username,
            i.recipient_number,
            send_date,
            str(i.uuid),
            i.status,
            i.status_message,
            gateway,
        ])

    data = tablib.Dataset(*list_val, headers=headers)

    if format_type == Export_choice.XLS:
        response.write(data.xls)
    elif format_type == Export_choice.CSV:
        response.write(data.csv)
    elif format_type == Export_choice.JSON:
        response.write(data.json)

    return response
