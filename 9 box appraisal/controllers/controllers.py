# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug.utils


class Appraisal(http.Controller):
    @http.route('/remove_list', auth='public', method='post', type='http',
                csrf=False)
    def remove(self, **post):
        list_id = request.env['employee.list'].search(
            [('name', '=', int(post['name'])),
             ('appraisal_name', '=', int(post['id']))])
        employee_value_id = request.env['appraisal.value'].search(
            [('employee_id', '=', int(post['name'])),
             ('name', '=', int(post['id'])),
             ('potential', '=', list_id.potential),
             ('performance', '=', list_id.performance)])
        if list_id:
            employee_priod__id = request.env['period'].search(
                [('id', '=', list_id.employee_period_id.id)])
            if employee_priod__id:
                employee_priod__id.update({'drop': False})
            values = {
                'potential_field': False,
                'performance_field': False,
                'period_id': False,
                'category': False
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', int(post['name']))])
            employee_id.update(values)
            list_id.unlink()
            employee_value_id.unlink()

    @http.route('/for_create_list', auth='public', method='post', type='http',
                csrf=False)
    def index(self, **post):
        print('running')
        if post['category'] == 'hp_lp':
            print('ckeni')
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'hp_mp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'hp_hp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'mp_lp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'mp_mp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'mp_hp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'lp_lp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'lp_mp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)
        if post['category'] == 'lp_hp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            list_id = request.env['employee.list'].search(
                [('appraisal_name', '=', period_id.id),
                 ('name', '=', int(post['name']))])
            if list_id:
                list_id.unlink()
            values = {
                'name': post['name'],
                'start_date': period_id.start_date,
                'end_date': period_id.end_date,
                'appraisal_name': period_id.id,
                'potential': post['potential'],
                'performance': post['performance'],
                'employee_period_id': post['employee']
            }
            req = request.env['employee.list'].create(values)

    @http.route('/update_employee', auth='public', method='post', type='http',
                csrf=False)
    def list(self, **post):
        if post['category'] == 'hp_lp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'hp_mp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id

            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            print('employee', employee_id)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            print('period_id', employee_period_id)
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'hp_hp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'mp_lp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', int(post['employee']))])
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'mp_mp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'mp_hp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})
        if post['category'] == 'lp_lp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'lp_mp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})

        if post['category'] == 'lp_hp':
            period_id = request.env['appraisal.period'].search(
                [('id', '=', post['appraisal'])])
            values = {
                'potential_field': post['potential'],
                'performance_field': post['performance'],
                'period_id': period_id.id
            }
            employee_id = request.env['hr.employee'].search(
                [('id', '=', post['name'])])
            employee_id.update(values)
            list = []
            val = {
                'name': post['appraisal'],
                'category': post['category'],
                'potential': post['potential'],
                'performance': post['performance'],
            }
            list.append((0, 0, val))
            employee_id.update({'appraisal_value_id': list})
            employee_period_id = request.env['period'].search(
                [('id', '=', post['employee'])])
            if employee_period_id:
                employee_period_id.update({'drop': True})

