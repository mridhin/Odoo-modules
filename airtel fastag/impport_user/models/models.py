# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
import base64
import csv
import io
import collections
import xlrd
from datetime import datetime

class ImportProduct(models.TransientModel):
    _name = "import.user"

    fastag_user = fields.Binary('Select File')
    filename = fields.Char('Select File')
    import_line_form = fields.One2many('user.details', 'import_user_id',
                                      string="All Users")

    def import_user_line(self):
        if self.fastag_user == False:
            raise UserError('Please Upload your csv first then imoport user')
        else:
            if self.filename.endswith('csv'):
                csv_data = base64.b64decode(self.fastag_user)
                string_data = csv_data.decode('utf-8')
                data_file = io.StringIO(string_data)
                data_file.seek(0)
                file_reader = []
                try:
                    csv_reader = csv.reader(data_file, delimiter=',')
                    next(csv_reader)
                    file_reader.extend(csv_reader)
                    terms = []
                    data = len(list(file_reader))
                    count = collections.Counter()
                    index = 1
                    for row_vals in file_reader:
                        employee_id = row_vals[4]
                        count[employee_id] += 1
                        for emp_id_count in count.items():
                            if emp_id_count[1] > 1:
                                raise UserError('Duplicate employee id found in the sheet')
                        index += 1
                        print(datetime.strptime(row_vals[6], '%d/%m/%Y'))
                        terms.append(
                                (0, 0, {'lapu_no': row_vals[0],
                                        'circle_id': row_vals[1],
                                        'project_id': row_vals[2],
                                        'work_city': row_vals[3],
                                        'emp_code': row_vals[4],
                                        'name': row_vals[5],
                                        'doj': datetime.strptime(row_vals[6], '%d/%m/%Y'),
                                        'office_add': row_vals[7],
                                        'designation': row_vals[8],
                                        'tl_name': row_vals[9],
                                        'cm_name': row_vals[10],
                                        'em_name': row_vals[11],
                                        'email': row_vals[12],
                                        'employee':row_vals[13],
                                        'promoter':row_vals[14],
                                        'password':row_vals[15]
                                        }))

                    self.sudo().update({'import_line_form': terms})
                    return {
                        'name': _('Import User'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'import.user',
                        'view_id': self.env.ref(
                            'impport_user.add_user_action_view').id,
                        'res_id': self.id,
                        'target': 'new'
                    }

                except csv.Error:
                    raise UserError("Cannot determine the file format for the attached file.")

            if self.filename.endswith('xlsx'):
                terms = []
                file_datas = base64.decodestring(self.fastag_user)
                workbook = xlrd.open_workbook(file_contents=file_datas)
                sheet = workbook.sheet_by_index(0)
                data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for
                        r in range(sheet.nrows)]
                data.pop(0)
                count = collections.Counter()
                print('count',count)
                for row_vals in data:
                    employee_id = row_vals[4]
                    count[employee_id] += 1
                    for emp_id_count in count.items():
                        if emp_id_count[1] > 1:
                            print(emp_id_count[1])
                            raise UserError(
                                'Duplicate employee id found in the sheet')
                    terms.append(
                        (0, 0, {'lapu_no': row_vals[0],
                                'circle_id': row_vals[1],
                                'project_id': row_vals[2],
                                'work_city': row_vals[3],
                                'emp_code': row_vals[4],
                                'name': row_vals[5],
                                'doj': row_vals[6],
                                'office_add': row_vals[7],
                                'designation': row_vals[8],
                                'tl_name': row_vals[9],
                                'cm_name': row_vals[10],
                                'em_name': row_vals[11],
                                'email': row_vals[12],
                                'employee': row_vals[13],
                                'promoter': row_vals[14],
                                'password': row_vals[15]
                                }))

                self.sudo().update({'import_line_form': terms})
                return {
                    'name': _('Import User'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.user',
                    'view_id': self.env.ref(
                        'impport_user.add_user_action_view').id,
                    'res_id': self.id,
                    'target': 'new'
                }

    def import_user(self):
        insert_user = []
        designation = dict(self.env['res.users']._fields['rs_designation'].selection)
        key_list = list(designation.keys())
        val_list = list(designation.values())
        for user_id in self.import_line_form:
            circle_query = """SELECT id FROM rs_circle_name WHERE name = %(name)s"""
            self.env.cr.execute(circle_query, {'name': user_id.circle_id
                                        })
            circle_id = self.env.cr.fetchall()
            position = val_list.index(user_id.designation)
            user_designation = key_list[position]
            em_id = self.env['res.users'].search(
                [('name','=',user_id.em_name)])
            cm_id = self.env['res.users'].search(
                [('name', '=', user_id.cm_name)])
            tl_id = self.env['res.users'].search(
                [('name', '=', user_id.tl_name)])
            # em_query = """SELECT id FROM res_users WHERE name = %(name)s"""
            # self.env.cr.execute(em_query, {'name': user_id.em_name
            #                             })
            # em_id = self.env.cr.fetchall()
            # cm_query = """SELECT id FROM res_users WHERE name = %(name)s"""
            # self.env.cr.execute(cm_query, {'name': user_id.cm_name
            #                             })
            # cm_id = self.env.cr.fetchall()
            # tl_query = """SELECT id FROM res_users WHERE name = %(name)s"""
            # self.env.cr.execute(tl_query, {'name': user_id.tl_name
            #                             })
            # tl_id = self.env.cr.fetchall()
            # partner_id = self.env['res.partner'].create({'name': "name"})
            user_insert_values = {
                                    'rs_lapu_no': user_id.lapu_no,
                                    'rs_circle': circle_id[0],
                                   'rs_project': user_id.project_id,
                                    'rs_work_city': user_id.work_city,
                                    'rs_employee_id': user_id.emp_code,
                                    'name': user_id.name,
                                    'rs_doj': user_id.doj,
                                    'rs_office_addres': user_id.office_add,
                'rs_designation': user_designation,
                'login':user_id.lapu_no,
                'rs_employee':user_id.employee,
                'rs_em':em_id.id,
                'rs_cm':cm_id.id,
                'rs_tl':tl_id.id,
                'rs_email':user_id.email,
                'password':user_id.password,
                'groups_id': [(6, 0, [(self.env.ref('stock.group_stock_user').id)])],
                'active': True

                                    }
            insert_user.append(user_insert_values)
            user_id = self.env['res.users'].sudo().create(user_insert_values)

        # insert_user_sql = """INSERT INTO res_users ( rs_lapu_no, rs_circle,rs_project,rs_work_city,
        # rs_employee_id, rs_doj,rs_office_addres,login,company_id,partner_id)
        # VALUES (%(rs_lapu_no)s,%(rs_circle)s, %(rs_project)s, %(rs_work_city)s,
        #  %(rs_employee_id)s,%(rs_doj)s, %(rs_office_addres)s,%(login)s,%(company_id)s,%(partner_id)s)"""
        #
        # self.env.cr.executemany(insert_user_sql,insert_user)


class UserDetails(models.TransientModel):
    _name = 'user.details'
    _description = 'User Details'

    lapu_no = fields.Char(string='Lapu No')
    circle_id = fields.Char(string="Circle")
    project_id = fields.Char(string='Project')
    work_city = fields.Char(string='Work City')
    emp_code = fields.Char(string='Employee ID')
    name = fields.Char(string='Name')
    doj = fields.Date(string="DOJ")
    office_add = fields.Text(string="Office Address ")
    designation = fields.Char(string="Designaion")
    tl_name = fields.Char(string="TL")
    cm_name = fields.Char(string="CM")
    email = fields.Char(string="Email")
    em_name = fields.Char(string="EM")
    import_user_id = fields.Many2one('import.user')
    employee = fields.Boolean()
    promoter = fields.Boolean()
    password = fields.Char()
class import_user(models.Model):
    _inherit = "res.users"

    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Odoo')],
        'Notification', required=False, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in Odoo: notifications appear in your Odoo Inbox")
