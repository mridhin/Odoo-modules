from werkzeug.utils import redirect

from odoo.osv import expression

from odoo.addons.account.controllers import portal
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
from odoo.exceptions import UserError, ValidationError
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from datetime import datetime

from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND, OR

from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager


class PortalTimesheetCustomerPortal(TimesheetCustomerPortal):

    def _get_searchbar_groupby(self):
        searchbar_groupby = super()._get_searchbar_groupby()
        searchbar_groupby.update(
            status={'input': 'status', 'label': _('status')},
            platform={'input': 'platform', 'label': _('Platform')})

        return searchbar_groupby

    def _get_search_domain(self, search_in, search):
        search_domain = super()._get_search_domain(search_in, search)
        if search_in in ('status', 'all'):
            search_domain = expression.OR(
                [search_domain, [('validated_status', 'ilike', search)]])
        if search_in in ('platform', 'all'):
            search_domain = expression.OR(
                [search_domain, [('area', 'ilike', search)]])

        return search_domain

    def _get_groupby_mapping(self):
        groupby_mapping = super()._get_groupby_mapping()
        groupby_mapping.update(
            status='validated_status',
            platform='area')
        return groupby_mapping

    def _get_searchbar_sortings(self):
        searchbar_sortings = super()._get_searchbar_sortings()
        searchbar_sortings.update(
            status={'label': _('Status'), 'order': 'validated_status'})
        return searchbar_sortings

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None,
                             search=None, search_in='status', groupby='status',
                             **kw):
        Timesheet = request.env['account.analytic.line']
        domain = Timesheet._timesheet_get_portal_domain()
        Timesheet_sudo = Timesheet.sudo()

        values = self._prepare_portal_layout_values()
        _items_per_page = 100

        searchbar_sortings = self._get_searchbar_sortings()

        searchbar_inputs = self._get_searchbar_inputs()

        searchbar_groupby = self._get_searchbar_groupby()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [
                ('date', '>=', date_utils.start_of(today, "week")),
                ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [
                ('date', '>=', date_utils.start_of(today, 'month')),
                ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [
                ('date', '>=', date_utils.start_of(today, 'year')),
                ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'),
                        'domain': [('date', '>=', quarter_start),
                                   ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [
                ('date', '>=', date_utils.start_of(last_week, "week")),
                ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [
                ('date', '>=', date_utils.start_of(last_month, 'month')),
                ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [
                ('date', '>=', date_utils.start_of(last_year, 'year')),
                ('date', '<=', date_utils.end_of(last_year, 'year'))]},
            'status': {'label': _('Approval Waiting'), 'domain': [
                ('validated_status', '=', 'approval_waiting')]},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            #--------------------------- if not request.env.user.employee_count:
                #---------------------------------------------- filterby = 'all'
            #------------------------------------------------------------- else:
            # Added default filter by this week value
            filterby = 'week'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        timesheet_count = Timesheet_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/timesheets",
            url_args={'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterby': filterby,
                      'groupby': groupby},
            total=timesheet_count,
            page=page,
            step=_items_per_page
        )

        def get_timesheets():
            groupby_mapping = self._get_groupby_mapping()
            field = groupby_mapping.get(groupby, None)
            orderby = '%s, %s' % (field, order) if field else order
            timesheets = Timesheet_sudo.search(domain, order=orderby,
                                               limit=_items_per_page,
                                               offset=pager['offset'])
            if field:
                if groupby == 'date':
                    time_data = Timesheet_sudo.read_group(domain, ['date',
                                                                   'unit_amount:sum'],
                                                          ['date:day'])
                    mapped_time = dict([(datetime.strptime(m['date:day'],
                                                           '%d %b %Y').date(),
                                         m['unit_amount']) for m in time_data])

                    grouped_timesheets = [
                        (Timesheet_sudo.concat(*g), mapped_time[k]) for k, g in
                        groupbyelem(timesheets, itemgetter('date'))]

                elif groupby == 'status':
                    time_data = Timesheet_sudo.read_group(domain,
                                                          ['validated_status',
                                                           'unit_amount:sum'],
                                                          ['validated_status'])
                    mapped_time = dict(
                        [(m['validated_status'], m['unit_amount'])
                         for m in time_data])

                    grouped_timesheets = [
                        (Timesheet_sudo.concat(*g), mapped_time[k]) for k, g in
                        groupbyelem(timesheets, itemgetter('validated_status'))]
                elif groupby == 'platform':
                    time_data = Timesheet_sudo.read_group(domain, ['area',
                                                                   'unit_amount:sum'],
                                                          ['area'])
                    mapped_time = dict(
                        [(m['area'], m['unit_amount'])
                         for m in time_data])

                    grouped_timesheets = [
                        (Timesheet_sudo.concat(*g), mapped_time[k]) for k, g in
                        groupbyelem(timesheets, itemgetter('area'))]
                else:
                    time_data = Timesheet_sudo.read_group(domain, [field,
                                                                   'unit_amount:sum'],
                                                          [field])
                    mapped_time = dict(
                        [(m[field][0] if m[field] else False, m['unit_amount'])
                         for m in time_data])
                    grouped_timesheets = [
                        (Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g
                        in groupbyelem(timesheets, itemgetter(field))]
                return timesheets, grouped_timesheets

            grouped_timesheets = [(
                timesheets,
                sum(Timesheet_sudo.search(domain).mapped('unit_amount'))
            )] if timesheets else []
            return timesheets, grouped_timesheets

        timesheets, grouped_timesheets = get_timesheets()

        values.update({
            'timesheets': timesheets,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'timesheet',
            'default_url': '/my/timesheets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'is_uom_day': request.env[
                'account.analytic.line']._is_timesheet_encode_uom_day(),
        })
        return request.render("hr_timesheet.portal_my_timesheets", values)
