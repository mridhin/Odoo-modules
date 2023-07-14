import werkzeug

from odoo import http, fields, tools, _
from odoo.http import request
import datetime
from odoo.addons.website.controllers.form import WebsiteForm
import json
from odoo.exceptions import ValidationError, UserError
from psycopg2 import IntegrityError

class WebsiteFormCustomize(WebsiteForm):
    def _handle_website_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search(
            [('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })

        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})

        try:
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            partner_obj = request.env['res.partner']
            partner_rec = partner_obj.sudo().search([('name', '=', data['record'].get('contact_name'))], limit=1)
            if not partner_rec:
                partner_rec = request.env['res.partner'].sudo().create({
                    'name': data['record'].get('contact_name'),
                })
            else:
                # partner record update
                partner_rec.sudo().write({
                    'name': data['record'].get('contact_name'),
                })
            if id_record:
                crm_id = request.env['crm.lead'].sudo().browse(id_record)
                if crm_id:
                    crm_dict = {
                        'tag_ids': [(4, int(kwargs.get('tag_ids')))],
                        'x_studio_awb_service_type_id': int(kwargs.get('x_studio_awb_service_type_id')),
                        'x_studio_area_id': int(kwargs.get('x_studio_area_id')),
                        'x_studio_preferred_time_slot': kwargs.get('x_studio_preferred_time_slot'),
                        'x_studio_preferred_service_schedule': kwargs.get('x_studio_preferred_service_schedule'),
                        'partner_id': partner_rec.id,
                        'x_studio_contact_no': kwargs.get('x_studio_contact_no'),
                        'x_studio_use_new_address': kwargs.get('x_studio_use_new_address'),
                        'x_studio_street': kwargs.get('x_studio_street'),
                        'x_studio_barangay': kwargs.get('x_studio_barangay'),
                        'x_studio_city_1': kwargs.get('x_studio_city_1'),
                        'x_studio_province': kwargs.get('x_studio_province'),
                        'x_studio_customer_name_1': kwargs.get('x_studio_customer_name_1'),
                    }
                    crm_id.sudo().write(crm_dict)
                self.insert_attachment(model_record, id_record, data['attachments'])
                # in case of an email, we want to send it immediately instead of waiting
                # for the email queue to process
                if model_name == 'mail.mail':
                    request.env[model_name].sudo().browse(id_record).send()

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})
class PortalUser(http.Controller):
    @http.route('/online_appointment', type='http', auth='public', website=True)
    def appointment_form(self, **kw):
        values = {}
        services = request.env["calendar.appointment.type"].sudo().search([])
        areas = []
        dates = []
        user_id = request.env.user
        user_partner_id = request.env["res.users"].search([('id', '=', user_id.id)]).partner_id.id
        philipines_id = request.env["res.country"].search([('name', '=', 'Philippines')])
        states = request.env["res.country.state"].search([('country_id', '=', philipines_id.id)],order='name asc')
        values.update({
            'services': services,
            'areas': areas,
            'dates': dates,
            # 'x_studio_customer_name_1': user_id.partner_id.name,
            'x_studio_contact_no': user_id.partner_id.mobile or user_id.partner_id.phone,
            'states': states,
            'partner_id': user_partner_id
        })
        return http.request.render("aserco_website_form.appointment_form", values)
    '''
       Added Function to Filter the area
    '''

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

    '''
           Added Function to Filter the available dates
        '''

    @http.route('/get_available_dates', type='http', auth='public', website=True)
    def get_available_dates(self, **kw):
        territory = request.env['x_territory']
        allocated_technician_line_64c6d = request.env['x_allocated_technician_line_64c6d']
        allocated_technician_line_64c6d = allocated_technician_line_64c6d.sudo().search(
            [('x_studio_service_type_id', '=', int(kw.get('service_type'))), ('x_studio_time_slot', '=', kw.get('timeslot'))])
        allocated_technician_line_64c6d = allocated_technician_line_64c6d.filtered(lambda tl: tl.x_studio_available_allocation > 0)
        allocated_technician = allocated_technician_line_64c6d.mapped('x_allocated_technician_id')
        territory = territory.sudo().search([('id', '=', int(kw.get('area')))])
        territory_technicians = territory.mapped('x_studio_technicians')
        today = datetime.datetime.now()
        day_thirty = today + datetime.timedelta(days=30)
        allocated_technician = allocated_technician.filtered(lambda al: al.x_studio_user_id in territory_technicians and al.x_studio_date > today.date() and al.x_studio_date <= day_thirty.date())
        allocated_technician = allocated_technician.sorted(key=lambda s: s.x_studio_date)

        available_dates_list = ["<option value=' '>select...</option>"]
        for aloc_tec in allocated_technician:
            option = "<option value="+aloc_tec.x_studio_date.strftime("%Y-%m-%d")+">" + aloc_tec.x_studio_date.strftime("%d-%B-%Y") + "</option>"
            # option = "<option value=" + str(aloc_tec.id) + ">" + aloc_tec.x_studio_date.strftime("%d-%B-%Y") + "</option>"
            if option in available_dates_list:
                continue
            available_dates_list.append(option)
        option_value = '%s' % ' '.join(map(str, available_dates_list))
        return option_value
