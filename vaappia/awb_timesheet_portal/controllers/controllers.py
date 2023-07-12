# -*- coding: utf-8 -*-

import logging
from werkzeug.utils import redirect
from odoo import fields, http, _
from odoo.http import request

_logger = logging.getLogger(__name__)
#imports of python lib
import xlrd
import io
import xlsxwriter 
import io
import xlsxwriter
import json
# imports of odoo
from werkzeug.utils import redirect
from odoo import fields, http, _
from odoo.http import request
from odoo import http
from odoo.http import content_disposition,request 
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo.tools import date_utils
from xlsxwriter.workbook import Workbook
from odoo.http import content_disposition, request
from odoo.tools import ustr, osutil


class WebTimesheetRequest(http.Controller):

    @http.route('/get/project/activity/id', method=['GET'], type='json',
                auth='user', website=True, csrf=False)
    def request_activity(self, **kw):
        activity_id = kw.get('activity_id')
        result = request.env['project.task'].sudo().search(
            [('id', '=', activity_id)])

        activity_type = {}

        for record in result:
            activity_type.update({
                'id': record.x_studio_activity_types_id.id,
                'name': record.x_studio_activity_types_id.x_name,
            })

        res = {
            'activity_type_rec': activity_type
        }
        return res

    @http.route('/get/employee/project/id', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def request_project(self, **kw):

        project_id = kw.get('project_id')
        result = request.env['project.project'].sudo().search(
            [('id', '=', project_id)])
        result_project_task = request.env['project.task'].sudo().search(
            [('user_ids', 'in', [request.env.user.id])])

        company_rec = {}
        project_dic = {}
        activity_list = []

        for record in result:
            company_rec.update({
                'id': record.partner_id.id,
                'name': record.partner_id.name
            })
            project_dic.update({
                'type': record.x_studio_project_scope_1
            })

        for record in result_project_task:
            if int(record.project_id.id) == int(project_id):
                activity_list.append({'id': record.id, 'name': record.name,
                                      'project_id': record.project_id.id})

        res = {
            'company_rec': company_rec,
            'project_rec': project_dic,
            'project_activity': activity_list
        }
        return res

    @http.route('/create/timesheets/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def request(self):
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        partner = request.env['res.partner'].sudo().search([])
        # project = request.env['project.project'].sudo().search([('collaborator_ids','in', True)])
        project_collaberator = request.env[
            'project.collaborator'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        tag_id = request.env['project.tags'].sudo().search([])
        employee_dict = []
        employee_rec = {}

        partner_dict = []
        project_dict = []
        activity_dict = []
        tag_dict = []
        for record in employee:
            employee_rec.update({
                'id': record.id,
                'name': record.name
            })
            # name = record.name
            # employee_dict.append({'id': record.id, 'name': name})
        for record in partner:
            partner_dict.append({'id': record.id, 'name': record.name})
        for record in project_collaberator:
            project_dict.append(
                {'id': record.project_id.id, 'name': record.project_id.name})
            # for record in activity:
            activity = request.env['project.task'].sudo().search(
                [('project_id', '=', record.project_id.id)])
            for record in activity:
                activity_dict.append({'id': record.id, 'name': record.name})
        for record in tag_id:
            tag_dict.append({'id': record.id, 'name': record.name})
        res = {
            'employee': employee_dict,
            'partner': partner_dict,
            'project': project_dict,
            'activity': activity_dict,
            'tag': tag_dict,
            'employee_rec': employee_rec
        }
        return res

    @http.route('/timesheet/request/submit', method='post', type='http',
                auth='public',
                website=True, csrf=False)
    def send_request(self, **post):
        values = {
            'employee_id': int(post['employee']),
            'date': post['date'],
            'project_id': int(post['project']),
            'task_id': int(post['activity']),
            'name': post['notes'],
            'unit_amount': float(post['hours']),
            'area': post['platform'],
            # 'timesheet_invoice_type': post['activity_type'],
            'x_studio_activity_types': post['activity_type'],
            'project_type': post['project_type']

        }
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        timesheet = request.env['account.analytic.line'].sudo().search(
            [('date', '=', post['date']), ('employee_id', '=', employee.id),
             ('validated_status', '!=', 'rejected')])
        if not timesheet:
            req = request.env['account.analytic.line'].sudo().create(values)
            #filter by current url value
            filter_by = post['url']
            return redirect('/my/timesheets'+filter_by)

    @http.route('/edit/request', method='post', type='http',
                auth='public',
                website=True, csrf=False)
    def edit_request(self, **post):
        id = int(post['timesheet'])
        values = {

            'date': post['date'],
            'name': post['name'],
            'unit_amount': post['hours']
        }
        req = request.env['account.analytic.line'].sudo().search(
            [('id', '=', id)])
        timesheet = request.env['account.analytic.line'].sudo().search(
            [('id', '!=', id),
             ('date', '=', post['date']),
             ('employee_id', '=', req.employee_id.id)])
        if not timesheet:
            req.update(values)
            #filter by current url value
            filter_by = post['url_name']
            return redirect('/my/timesheets'+filter_by)

    @http.route('/approve/timesheets/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def approve_record(self, **kw):
        timesheet_id = kw.get('checked')
        for rec in timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().search(
                [('id', '=', int(rec))])
            if request.env.user.id == timesheet.project_id.user_id.id:
                if timesheet.project_id.x_studio_project_scope_1 == "External":
                    for obj in timesheet:
                        obj.sudo().write(
                            {'client_approval': True, 'submitted': False,
                             'validated_status': 'approval_waiting'})
                if timesheet.project_id.x_studio_project_scope_1 == "Internal":
                    for obj in timesheet:
                        obj.sudo().write({'validated': True, 'submitted': False,
                                          'validated_status': 'validated'})
            if request.env.user.partner_id.id == timesheet.project_id.partner_id.id:
                for obj in timesheet:
                    obj.sudo().write(
                        {'validated': True, 'client_approval': False,
                         'validated_status': 'validated'})
        return True

    @http.route('/reject/timesheets/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def reject_record(self, **kw):
        timesheet_id = kw.get('checked')
        result = ""
        for rec in timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().search(
                [('id', '=', int(rec))])
            if timesheet:
                for obj in timesheet:
                    if obj.validated_status != 'validated':
                        obj.write(
                            {'rejected': True, 'submitted': False,
                             'validated_status': 'rejected'})
                        result = "true"
                    else:
                        result = "false"
                        return False
        return {
            'result': result
        }

    @http.route('/delete/timesheets/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def delete_record(self, **kw):
        timesheet_id = kw.get('checked')
        result = ""
        for rec in timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().search(
                [('id', '=', int(rec))])
            if timesheet.validated_status == "draft":
                timesheet.unlink()
                result = "true"
            else:
                result = "false"
                return False
        return {
            'result': result
        }

    @http.route('/submit/timesheets/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def submit_record(self, **kw):
        timesheet_id = kw.get('checked')
        total_hours = 0
        result = ""
        for rec in timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().search(
                [('id', '=', int(rec))])
            if timesheet.validated_status == "draft":
                total_hours += int(timesheet.unit_amount)

        if total_hours >= 40:
            for obj in timesheet_id:
                timesheet = request.env['account.analytic.line'].sudo().search(
                    [('id', '=', int(obj))])
                timesheet.write(
                    {'submitted': True, 'validated_status': 'submit'})
            result = "true"

        else:
            result = "false"
        res = {'result': result}
        return res

    @http.route('/usecheck/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def check_user(self):
        employee = request.env['hr.employee'].sudo().search([])
        employee_list = []
        employee_check = "false"
        for rec in employee:
            employee_list.append(rec.user_id.id)
        if request.env.user.id in employee_list:
            employee_check = "true"
        res = {
            'employee': employee_check

        }
        return res

    @http.route('/edit/timesheets/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def edit_record(self, **kw):
        timesheet_dict = []
        timesheet_id = kw.get('checked')
        timesheet = request.env['account.analytic.line'].sudo().search(
            [('id', '=', int(timesheet_id[0]))])
        for record in timesheet:
            timesheet_dict.append({'id': record.id, 'name': record.name,
                                   'date': record.date,
                                   'hours': timesheet.unit_amount
                                      , 'state': record.validated_status})

        res = {
            'timesheet': timesheet_dict

        }
        return res

    @http.route('/update/request', method='post', type='http',
                auth='public',
                website=True, csrf=False)
    def update_reject_record(self, **post):
        id = int(post['timesheet'])
        values = {
            #'name': post['name'],
            'approver_notes': post['name'],
            'validated_status': 'rejected',
            'submitted': False,
            'rejected': True
        }
        req = request.env['account.analytic.line'].sudo().search(
            [('id', '=', id)])
        #if req.validated_status != 'validated':
        req.update(values)
        # Get current url value
        link_val = request.httprequest.__dict__
        http_refer = link_val['environ']['HTTP_REFERER']
        return redirect(http_refer)

    @http.route('/check/date/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def check_date_record(self, **kw):
        timesheet_result = ""
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        timesheet_date = kw.get('date')
        timesheet = request.env['account.analytic.line'].sudo().search(
            [('date', '=', timesheet_date), ('employee_id', '=', employee.id),
             ('validated_status', '!=', 'rejected')])
        if timesheet:
            timesheet_result = "true"
        else:
            timesheet_result = "false"
        res = {
            'timesheet': timesheet_result

        }
        return res

    @http.route('/check/update/date/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def check_update_date_record(self, **kw):
        timesheet_result = ""
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        timesheet_date = kw.get('date')
        timesheet_id = kw.get('id')
        timesheet = request.env['account.analytic.line'].sudo().search(
            [('date', '=', timesheet_date), ('employee_id', '=', employee.id),
             ('validated_status', '!=', 'rejected'),
             ('id', '!=', int(timesheet_id))])
        if timesheet:
            timesheet_result = "true"
        else:
            timesheet_result = "false"
        res = {
            'timesheet': timesheet_result

        }
        return res

    @http.route('/time/total', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def total_time(self, **kw):
        timesheet = kw.get('checked')
        total_hours = 0
        new_hour = 0
        result = ""
        check_id = 0
        first_timesheet_id = request.env['account.analytic.line'].sudo().search(
            [('id', '=', int(timesheet[-1]))])
        date = first_timesheet_id.date
        start = date_utils.start_of(date, "week")
        end = date_utils.end_of(date, 'week')
        for rec in timesheet:
            timesheet_id = request.env['account.analytic.line'].sudo().search(
                [('id', '=', int(rec))])
            total_hours += int(timesheet_id.unit_amount)
            if int(timesheet[-1]) != int(rec):
                if not start <= timesheet_id.date <= end:
                    result = "false"
                    check_id = timesheet_id.id
                    total_hours = total_hours - int(timesheet_id.unit_amount)
                    new_hour = int(timesheet_id.unit_amount)
        res = {
            'total': total_hours,
            'result': result,
            'check_id': check_id,
            'new_hour': new_hour
        }
        return res

    @http.route('/create/pdf/records', method='post', type='http',
                auth='public',
                website=True, csrf=False)
    def create_pdf_request(self, **post):
        pdf = request.env['account.analytic.line'].sudo().create_pdf()
        pdfhttpheaders = [('Content-Type', 'application/pdf'),
                          ('Content-Length', len(pdf['context']))]
        return request.make_response(pdf['context'])

    @http.route('/export/timesheets/records', methods=['POST'], type='http',
                auth='user', website=True, csrf=False)
    def export_record(self, **kw):
        timesheet_id = kw.get('checked')
        
        if timesheet_id:
            t_id = timesheet_id.split(",")
            s =[];
            for rec in t_id:
                timesheet = request.env['account.analytic.line'].sudo().search(
                    [('id', '=', int(rec))])
                
                date_format = str(timesheet.date)
                
                try:
                    s_dict ={}
                    s_dict['date']= date_format
                    s_dict['employee']= timesheet.employee_id.name
                    s_dict['project']= timesheet.project_id.name
                    s_dict['task']= timesheet.task_id.name 
                    s_dict['description']= timesheet.name 
                    s_dict['hours']= timesheet.unit_amount
                    project_type = lambda x : x if x else ''
                    s_dict['project_type']= project_type(timesheet.project_type)
                    activity_type  = lambda x : x if x else ''
                    s_dict['activity_type']= activity_type(timesheet.timesheet_invoice_type)
                    area  = lambda x : x if x else ''
                    s_dict['platform']= area(timesheet.area)
                    validated_status  = lambda x : x if x else ''
                    s_dict['status']= validated_status(timesheet.validated_status)
                   
                    s.append(s_dict)
                    
                    
                except Exception as e:
                    se = _serialize_exception
                 
            return str(s) 

