# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect


class WebMaintenanceRequest(http.Controller):
    @http.route(['/maintenance_request'], method='post', type='http',
                auth='user', website=True)
    def request(self):
        maintenance_equipment = request.env[
            'maintenance.equipment'].search([])
        maintenance_team = request.env['maintenance.team'].search([])
        employee = request.env['hr.employee'].search([])
        print(employee)
        request_dict = []
        team_name = []
        employee_dict = []
        for record in maintenance_equipment:
            name = record.name
            request_dict.append({'id': record.id, 'name': name})
        for record in maintenance_team:
            name = record.name
            team_name.append({'id': record.id, 'name': name})
        for record in employee:
            name = record.name
            employee_dict.append({'id': record.id, 'name': name})

        return http.request.render('web_maintenance_request.Maintenance', {
            'equipment_selection': request_dict,
            'team_selection': team_name,
            'employee': employee_dict
        })

    @http.route('/submit', method='post', type='http', auth='public',
                website=True, csrf=False)
    def send_request(self, **post):
        values = {
            'name': post['subject'],
            'equipment_id': int(post['equipment']),
            'maintenance_team_id': int(post['teams']),
            'description': post['details'],
            'priority': post['stars'],
            'employee_id': int(post['employee'])
        }
        req = request.env['maintenance.request'].create(values)
        template = request.env.ref(
            'web_maintenance_request.mail_template_maintenance_request')
        template.send_mail(req.id, force_send=True)
        return redirect('/maintenance_request-thanks')
