# -*- coding: utf-8 -*-
# from odoo import http
import logging
from odoo import http, fields, tools, _
from odoo.http import request
import datetime
# from datetime import date, timedelta

_logger = logging.getLogger(__name__)


class BookingPageController(http.Controller):

    @http.route("/booking", type='http', auth='public', website=True)
    def customer_testimonial(self, **post):
        values = {}
        services = request.env["calendar.appointment.type"].sudo().search([])
        areas = request.env['x_territory'].sudo().search([])
        # areas = []
        dates = []
        partner_id = False
        user_id = request.env.user
        if request.session.uid and user_id:
            partner_id = user_id.partner_id
            cities = request.env["res.state.city"].sudo().search([('state_id', '=', partner_id.state_id.id)],
                                                                 order='name asc')
            barangays = request.env["res.city.barangay"].sudo().search(
                [('city_id', '=', partner_id.partner_city_id.id)], order='name asc')
            user_partner_id = request.env["res.users"].search([('id', '=', user_id.id)]).partner_id.id
        philipines_id = request.env["res.country"].search([('name', '=', 'Philippines')])
        states = request.env["res.country.state"].search([('country_id', '=', philipines_id.id)], order='name asc')

        service_id = False
        if post.get('service_id'):
            service_id = services.browse(int(post.get('service_id')))
        values.update({
            'services': services,
            'service_id': service_id if service_id else '',
            'areas': areas,
            'dates': dates,
            # 'x_studio_customer_name_1': user_id.partner_id.name,
            'x_studio_contact_no': user_id.partner_id.mobile or user_id.partner_id.phone,
            'states': states,
            'cities': cities if partner_id else None,
            'barangays': barangays if partner_id else None,
            'partner_id': user_partner_id if partner_id else None,
            'fname': partner_id.name if partner_id else None,
            'first_name': partner_id.first_name if partner_id else None,
            'middle_name': partner_id.middle_name if partner_id else None,
            'last_name': partner_id.last_name if partner_id else None,
            'email': partner_id.email if partner_id else None,
            'code': partner_id.country_id.phone_code if partner_id and partner_id.country_id else None,
            'mobile': partner_id.mobile.replace(" ", "")[3:] if partner_id and partner_id.mobile else None,
            'street': partner_id.street if partner_id else None,
            'partner_state': partner_id.state_id if partner_id else None,
            'partner_city': partner_id.partner_city_id if partner_id else None,
            'partner_barangay': partner_id.barangay_id if partner_id else None

        })
        return request.render("awb_customer_booking_page.customer_booking_page", values)

    @http.route('/get_city', type='http', auth='public', website=True)
    def get_city(self, **kw):
        """
        it is used to get cities of selected state
        """
        # city = request.env['res.state.city'].sudo()
        # region = int(kw.get('region'))
        # territory = request.env['x_territory'].sudo().search([('id','=',region)])
        # provience_id = request.env['res.country.state'].sudo().search([('name','ilike',territory.x_name)])
        # provience_id = provience_id.filtered(lambda p: p.city_ids)
        # city_ids = city.search([('state_id', '=', provience_id.id)],order='name asc')
        # city_list = []
        # for city in city_ids:
        #     option = "<option value= " + str(city.id) + ">" + city.name + "</option>"
        #     city_list.append(option)
        # option_value = '%s' % ' '.join(map(str, city_list))
        # return option_value
        state = request.env['res.country.state'].sudo()
        if kw.get('region'):
            region = int(kw.get('region'))
            provience_id = state.sudo().browse(region)
            if provience_id.exists():
                city_ids = provience_id.city_ids
                city_list = ["<option></option>"]
                for city in city_ids:
                    option = "<option value= " + str(city.id) + ">" + city.name + "</option>"
                    city_list.append(option)
                option_value = '%s' % ' '.join(map(str, city_list))
        else:
            option_value = '%s' % ' '.join(map(str, ["<option value=' '>Select...</option>"]))
        return option_value

    @http.route('/get_default_city', type='http', auth='public', website=True)
    def get_default_city(self, **kw):
        """
        it is used to get cities of selected state
        """
        city = request.env['res.state.city'].sudo()
        if kw.get('partner_id'):
            partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
            if partner_id and partner_id.partner_city_id:
                city_ids = city.search([('state_id', '=', partner_id.state_id.id)], order='name asc')
                city_list = ["<option value=' '>select...</option>"]
                for city in city_ids:
                    if city == partner_id.partner_city_id:
                        option = "<option selected value= " + str(city.id) + ">" + city.name + "</option>"
                    else:
                        option = "<option value= " + str(city.id) + ">" + city.name + "</option>"
                    city_list.append(option)
                option_value = '%s' % ' '.join(map(str, city_list))
                return option_value

    @http.route('/get_barangay', type='http', auth='public', website=True)
    def get_barangay(self, **kw):
        """
        it is used to get barangay of selected city
        """
        barangay_obj = request.env['res.city.barangay'].sudo()
        city = int(kw.get('city'))
        barangayes = barangay_obj.search([('city_id', '=', city)], order='name asc')
        barangay_list = ["<option></option>"]
        for barangay in barangayes:
            if barangay.name:
                option = "<option value= " + str(barangay.id) + ">" + barangay.name + "</option>"
            barangay_list.append(option)
        option_value = '%s' % ' '.join(map(str, barangay_list))
        return option_value

    @http.route('/get_default_barangay', type='http', auth='public', website=True)
    def get_default_barangay(self, **kw):
        """
        it is used to get barangay of selected city
        """
        barangay_obj = request.env['res.city.barangay'].sudo()
        if kw.get('partner_id'):
            partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
            if partner_id and partner_id.barangay_id:
                barangayes = barangay_obj.search([('city_id', '=', partner_id.partner_city_id.id)], order='name asc')
                barangay_list = ["<option value=' '>select...</option>"]
                for barangay in barangayes:
                    if barangay == partner_id.barangay_id:
                        print("get selected barangay", barangay.name)
                        option = "<option selected value= " + str(barangay.id) + ">" + barangay.name + "</option>"
                    else:
                        option = "<option value= " + str(barangay.id) + ">" + barangay.name + "</option>"
                    barangay_list.append(option)
                option_value = '%s' % ' '.join(map(str, barangay_list))
                return option_value

    @http.route('/get_area', type='http', auth='public', website=True)
    def get_area(self, **kw):
        allocated_technician_line_64c6d = request.env['x_allocated_technician_line_64c6d']
        territory = request.env['x_territory']
        allocated_technician_line_64c6d = allocated_technician_line_64c6d.sudo().search(
            [('x_studio_service_type_id', '=', int(kw.get('service_type')))])

        area_list = ["<option value=' '>select...</option>"]
        for tec in allocated_technician_line_64c6d:
            territories = territory.sudo().search(
                [('x_studio_technicians', 'in', tec.x_allocated_technician_id.x_studio_user_id.id)])
            for territory in territories:
                option = "<option value= " + str(territory.id) + ">" + territory.x_name + "</option>"
                if option in area_list:
                    continue
                area_list.append(option)
        option_value = '%s' % ' '.join(map(str, area_list))
        return option_value

    @http.route('/get_province', type='http', auth='public', website=True)
    def get_province(self, **kw):
        territory = request.env['x_territory'].sudo()
        territory_id = False
        if kw.get('partner_id'):
            partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
            if partner_id:
                territory_id = territory.search([('x_studio_state_ids', '=', partner_id.state_id.id)])

        area_list = ["<option value=' '>select...</option>"]
        territories = territory.search([])
        for territory in territories:
            if territory == territory_id:
                option = "<option selected value= " + str(territory.id) + ">" + territory.x_name + "</option>"
            else:
                option = "<option value= " + str(territory.id) + ">" + territory.x_name + "</option>"
            if option in area_list:
                continue
            area_list.append(option)
        option_value = '%s' % ' '.join(map(str, area_list))
        return option_value

    @http.route('/booking-success', type='http', auth='public', website=True, csrf=False)
    def booking_success(self, **kwargs):
        try:
            crm_obj = request.env['crm.lead'].sudo()
            city_obj = request.env['res.state.city'].sudo()
            barangay_obj = request.env['res.city.barangay'].sudo()
            city = False
            barangay = False
            if kwargs['city']:
                city = city_obj.search([('id', '=', int(kwargs['city']))], order='name asc')
            if kwargs['barangay']:
                barangay = barangay_obj.search([('id', '=', int(kwargs['barangay']))], order='name asc')
            if kwargs['x_studio_area_id']:
                provice_obj = request.env['res.country.state'].sudo().search([('id', '=', int(kwargs['x_studio_area_id']))])
            if kwargs['x_studio_awb_service_type_id']:
                service = request.env["calendar.appointment.type"].sudo().search(
                    [('name', '=', kwargs['x_studio_awb_service_type_id'])])

            preferred_service_date = datetime.datetime.strptime(kwargs['date_start'],
                                                                "%m/%d/%Y") if 'date_start' in kwargs else None

            vals = {
                'name': kwargs['fname'] + ' ' + kwargs['lname'],
                'last_name': kwargs['lname'],
                'first_name': kwargs['fname'],
                'appointment_type': int(kwargs['x_studio_awb_service_type_id']) or service.id,
                'state_id': int(kwargs['x_studio_area_id']),
                'city': city.name if city else '',
                'barangay': barangay.name if barangay else '',
                'mobile': kwargs['code'] + ' ' + kwargs['mobile'],
                'contact_name': kwargs['fname'] + ' ' + kwargs['lname'],
                'street': kwargs['street'],
                'email_from': kwargs['email'],
                'prefer_time_slot': kwargs['options'],
                'x_studio_preferred_time_slot': kwargs['options'].upper(),
                'x_studio_city_1': city.name if city else '',
                'x_studio_barangay': barangay.name if barangay else '',
                'x_studio_street': kwargs['street'],
                'x_studio_province': provice_obj.id,
                'x_studio_awb_service_type_id': int(kwargs['x_studio_awb_service_type_id']),
                'x_studio_customer_name_1': kwargs['lname'],
                'x_studio_contact_no': kwargs['mobile'] if kwargs['mobile'] else '',
                'x_studio_source_of_booking': 'Web Booking',
                'service_date': preferred_service_date,
                'type': 'opportunity' if preferred_service_date else 'lead'
            }
            lead = crm_obj.create(vals)
            return http.request.render("awb_customer_booking_page.customer_booking_success", kwargs)

        except Exception as e:
            _logger.error(f'Booking Success Error:: Error has encountered: {e}. Redirecting to booking page.')
            return request.redirect('/booking')

    @http.route('/get_booking/available_dates', type='http', csrf=False, auth='public', website=True)
    def get_booking_available_date(self, **kw):
        if not all(kw.get(param) for param in ['service_type', 'region', 'timeslot']):
            return ""
        state = request.env['res.country.state'].sudo().search([('id', '=', int(kw.get('region')))])
        territory = request.env['x_territory'].sudo().search([('x_name', '=', state.name)])
        territory_technicians = territory.mapped('x_studio_technicians')

        allocated_technician_lines = request.env['x_allocated_technician_line_64c6d'].sudo().search([
            ('x_studio_service_type_id', '=', int(kw['service_type'])),
            ('x_studio_time_slot', '=', kw['timeslot'].upper()),
            ('x_allocated_technician_id.x_studio_user_id', 'in', territory_technicians.ids),
            ('x_allocated_technician_id.x_studio_date', '>', fields.Datetime.now().date()),
            ('x_allocated_technician_id.x_studio_for_website_booking', '=', True)
            # ('x_allocated_technician_id.x_studio_date', '<=', fields.Datetime.now().date() + timedelta(days=30)),
        ])

        allocated_technician_lines = allocated_technician_lines.filtered(
            lambda tl: tl.x_studio_available_allocation > 0)

        allocated_technician = allocated_technician_lines.mapped('x_allocated_technician_id')

        available_dates = {allocation.x_studio_date.strftime('%-d-%-m-%Y') for allocation in allocated_technician}
        return ','.join(available_dates)

