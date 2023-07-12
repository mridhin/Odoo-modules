# -*- coding: utf-8 -*-
###################################################################################
#
#    Redian Software Pvt. Ltd
#
#    Copyright (C) 2019-TODAY Redian Software(<https://www.rediansoftware.com/>).
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api, _
import base64
import xlrd
import tempfile
import binascii
import io
import logging

_logger = logging.getLogger(__name__)
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError, RedirectWarning, Warning
import openpyxl
from openpyxl import load_workbook
from io import BytesIO
import csv
import subprocess
# from pyexcel_ods import get_data
import codecs


class OrderLineProduct(models.TransientModel):
    _name = "order.line.product"

    fastag_product = fields.Binary('Select File')
    filename = fields.Char('Select File')
    order_line_form = fields.One2many('fastag.line.form', 'product_line_id',
                                      string="All Fastags")
    user_id = fields.Many2one('res.users', string="User",
                              default=lambda self: self.env.user.id)
    picking_id = fields.Many2one('stock.picking', "Picking",
                                 ondelete='cascade')

    def upload_product_line(self):
        if self.fastag_product == False:
            raise UserError(
                _('Please Upload your excel first then imoport fastag'))
        else:
            if not self.filename.endswith('csv'):
                raise UserError(
                    _('Please Upload csv file'))
            csv_data = base64.b64decode(self.fastag_product)
            string_data = csv_data.decode('utf-8')
            data_file = io.StringIO(string_data)
            data_file.seek(0)
            file_reader = []
            try:
                csv_reader = csv.reader(data_file, delimiter=',')
                next(csv_reader)
                file_reader.extend(csv_reader)
                data = len(list(file_reader))
                picking_id = self.env['stock.picking'].browse(
                    self._context.get('active_id', False))
                today = date.today()
                lst_date = str(today).split("-")
                today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
                terms = []
                assigned_id = ''
                circle_id = ''
                consignment = ''
                dp = ''
                for row_vals in file_reader:
                    if picking_id:
                        if assigned_id == '':
                            assigned_id = self.env['res.users'].sudo().search(
                                [('login', '=', row_vals[5])])
                            if assigned_id:
                                consignment = str(row_vals[3])
                                dp = str(row_vals[4])
                                circle = self.env['rs.circle.name'].search(
                                    [('name', '=', str(row_vals[1]))])
                                circle_id = circle
                                if assigned_id.rs_designation == 'em':
                                    listids = []
                                    for each in assigned_id.rs_circle_ids:
                                        listids.append(each.id)
                                    if circle_id.id not in listids:
                                        raise UserError(
                                            _('Mismatching circle name'))
                                elif assigned_id.rs_circle.id != circle_id.id:
                                    raise UserError(
                                        _('Mismatching circle name'))

                                if data > 101 and assigned_id.rs_designation == 'fastag_promoter':
                                    raise UserError(
                                        _('You are not allowed to trasfer more then 100 fastag !'))

                                if data > 1001 and assigned_id.rs_designation == 'fastag_tl':
                                    raise UserError(
                                        _('You are not allowed to trasfer more then 1000 fastag !'))

                                if assigned_id.rs_designation == 'fastag_promoter':
                                    records = self.env[
                                        'product.template'].sudo().search_count(
                                        [('product_assigned_to', '=',
                                          assigned_id.id),
                                         ('fastag_sold', '=', 'no'),
                                         ('rs_faulty_stag', '=', 'no'),
                                         ('unlink_fastag', '=', False)])

                                    fastags_needed = int(records) + data
                                    if int(records) >= 100:
                                        raise UserError(
                                            _('Promoter %s fastag count is exceeds the limit 100',
                                              assigned_id.name))
                                    elif int(fastags_needed) > 100:
                                        raise UserError(
                                            _('Promoter %s Already there are %s FASTag you can assign %s !',
                                              assigned_id.name, int(records),
                                              100 - records))

                                if assigned_id.rs_designation == 'fastag_tl':
                                    records = self.env[
                                        'product.template'].sudo().search_count(
                                        [('product_assigned_to', '=',
                                          assigned_id.id),
                                         ('fastag_sold', '=', 'no'),
                                         ('rs_faulty_stag', '=', 'no'),
                                         ('unlink_fastag', '=', False)])

                                    fastags_needed = int(records) + data
                                    if int(records) >= 1000:
                                        raise UserError(
                                            _('Team leader %s fastag count is exceeds the limit 1000',
                                              assigned_id.name))
                                    elif int(fastags_needed) >= 1000:
                                        raise UserError(
                                            _('Team leader %s Already there are %s FASTag you can assign %s !',
                                              assigned_id.name, int(records),
                                              1000 - records))
                            else:
                                raise UserError(
                                    _('Please check the assignee mobile number'))
                        if assigned_id.login == row_vals[5]:
                            query = """
                                                                 SELECT *
                                                  				  FROM product_product pp
                                                    			 LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                                                				     WHERE pp.barcode = %(barcode)s AND pt.warehouse_emp_no = %(emp)s
                                                    		 AND pt.fastag_sold = 'no' AND pt.rs_faulty_stag = 'no' AND pt.unlink_fastag IS NOT TRUE
                                                         """
                            self.env.cr.execute(query,
                                                {'barcode': str(row_vals[0]),
                                                 'emp': self.env.user.rs_employee_id
                                                 })
                            product_ids = self.env.cr.fetchall()
                            print(product_ids)
                            list_rec = []
                            for rec in product_ids:
                                print(rec)
                                list_rec.append(rec[8]
                                                )
                            if str(row_vals[0]) not in list_rec:
                                raise UserError(
                                    _('%s Barcode is not available in the Products !',
                                      str(row_vals[0])))
                            for product_id in product_ids:
                                print(product_id[4])
                                terms.append(
                                    (0, 0, {'picking_id': picking_id.id,
                                            'product_id': product_id[0],
                                            'fatag_bracode': product_id[8],
                                            'circle_name': circle_id.name,
                                            'date_of_dispatch': today,
                                            'consignment_no': consignment,
                                            'delivery_partner': dp,
                                            'emp_mobile_no': assigned_id.login,
                                            'category_id': product_id[28]
                                            }))
                        else:
                            raise UserError(
                                _('Please check the assignee mobile number'))

                self.sudo().update({'order_line_form': terms})

                query = """UPDATE stock_picking
                                                                           SET rs_emp_no = %(emp)s,
                                                                               rs_destination_id = %(dest)s,
                                                                               rs_circle_id = %(circle)s,
                                                                               rs_state = 'assign'
                                                                            WHERE id = %(name)s """
                self.env.cr.execute(query, {'emp': assigned_id.login,
                                            'dest': assigned_id.id,
                                            'circle': circle_id.id,
                                            'name': picking_id.id
                                            })
                return {
                    'name': _('Product Selection'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'order.line.product',
                    'view_id': self.env.ref(
                        'rn_vehical_class.add_product_in_line_form_view').id,
                    'res_id': self.id,
                    'target': 'new'
                }

            except csv.Error:
                raise UserError(
                    _("Cannot determine the file format for the attached file."))

    def set_fastag_move_details(self):
        today = date.today()
        lst_date = str(today).split("-")
        today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
        picking_id = self.env['stock.picking'].browse(
            self._context.get('active_id', False))
        circle_id = ''
        assigned_id = ''
        stock_move_update = []
        product_update = []
        for line in self.order_line_form:
            if circle_id == '':
                circle_id = self.env['rs.circle.name'].search(
                    [('name', '=', line.circle_name)])
                print(circle_id.id)
                if not circle_id:
                    raise ValidationError(
                        _(' Please Create Proper Circle Name %s Is Not Given In The List!',
                          line.circle_name))
                    circle_id = self.env['rs.circle.name'].create(
                        {'name': line.circle_name})

            if assigned_id == '':
                assigned_id = self.env['res.users'].sudo().search(
                    [('login', '=', line.emp_mobile_no)])
            stock = self.env['stock.move'].sudo().create({})
            values = {'product_id': line.sudo().product_id.id,
                        'fatag_bracode':line.fatag_bracode,
                      'circle_name': circle_id.id,
                      'consignment_no': line.consignment_no,
                      'delivery_partner': line.delivery_partner,
                      'emp_mobile_no': line.emp_mobile_no,
                      'name': line.sudo().product_id.name,
                      'product_uom': line.sudo().product_id.uom_id.id,
                      'location_id': 24,
                      'picking_id': line.picking_id.id,
                      'location_dest_id': 24,
                      'category_id': line.category_id.id,
                      'id': stock.id

                      }
            stock_move_update.append(values)

            product_update_values = {
                'emp': 'Null',
                'id': line.sudo().product_id.product_tmpl_id.id,
                'assign': assigned_id.id}
            product_update.append(product_update_values)

        query1 = """UPDATE stock_move SET product_id=%(product_id)s, 
                                                fatag_bracode = %(fatag_bracode)s,
                                              circle_name=%(circle_name)s, 
                                              consignment_no=%(consignment_no)s,
                                              delivery_partner=%(delivery_partner)s, 
                                              emp_mobile_no=%(emp_mobile_no)s, 
                                              name=%(name)s, 

                                                product_uom=%(product_uom)s, 
                                                location_id=%(location_id)s,
                                                picking_id=%(picking_id)s,
                                                location_dest_id=%(location_dest_id)s,
                                                category_id=%(category_id)s
                                                WHERE id = %(id)s 
                     """
        self.sudo().env.cr.executemany(query1, stock_move_update)

        query = """UPDATE product_template
                                               SET warehouse_emp_no = %(emp)s,
                                               product_assigned_to = %(assign)s
                                                WHERE id = %(id)s """
        self.sudo().env.cr.executemany(query, product_update)

        if not self.order_line_form:
            raise UserError(_('You can not confirm empty fastag !'))
        template = self.env.ref(
            'rn_vehical_class.inventory_trasfer_assigned_email_template')
        print("======", template.email_to, self.id)
        self.env['mail.template'].browse(template.id).send_mail(
            self.order_line_form[0].picking_id.id)

        return True


class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Char('Message', readonly=True, required=True)

    # @api.multi
    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}


class FastagLineForm(models.TransientModel):
    _name = 'fastag.line.form'

    product_line_id = fields.Many2one('order.line.product', string="Order Line")
    product_id = fields.Many2one('product.product', string="Products",
                                 store=True)
    picking_id = fields.Many2one('stock.picking', "Picking",
                                 required=True, ondelete='cascade')
    fatag_bracode = fields.Char(string="FASTAG BARCODE")
    circle_name = fields.Char(string="CIRCLE NAME")
    date_of_dispatch = fields.Char(string="DATE OF DISPATCH")
    consignment_no = fields.Char(string="CONSIGNMENT NO")
    delivery_partner = fields.Char(string="DELIVERY PARTNER")
    emp_mobile_no = fields.Char(string="EMP MOB NO")
    category_id = fields.Many2one('product.category', string="TAG CLASS")
    move_line_id = fields.Many2one('seequence.wizard')

class CheckWizard(models.TransientModel):
    _name = 'product.sold'

    fastag_product = fields.Binary('Select File')
    filename = fields.Char('Select File')


    def product_update_line(self):
        if self.fastag_product == False:
            raise UserError(_('Please Upload your excel'))
        else:
            if not self.filename.endswith('csv'):
                raise UserError(_('Please Upload csv file'))
        csv_data = base64.b64decode(self.fastag_product)
        string_data = csv_data.decode('utf-8')
        data_file = io.StringIO(string_data)
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=',')
        next(csv_reader)
        file_reader.extend(csv_reader)
        data = len(list(file_reader))
        for row_vals in file_reader:
            product = self.env['product.template'].search([('barcode', '=', row_vals[0])])
            print('333333333',row_vals[0])
            if product:
                product.sudo().update({'fastag_sold': 'yes'})
            transfer_id = self.env['all.transfer.report'].search([('name', '=', row_vals[0])])
            transfer_id.sudo().write({'rs_tag_sold': 'yes'})
            move_id = self.env['stock.move'].search([('fatag_bracode', '=', row_vals[0])])
            for rec in move_id:
                rec.sudo().update({'fastag_sold': 'yes'})


# # -*- coding: utf-8 -*-
# ###################################################################################
# #
# #    Redian Software Pvt. Ltd
# #
# #    Copyright (C) 2019-TODAY Redian Software(<https://www.rediansoftware.com/>).
# #    This program is free software: you can modify
# #    it under the terms of the GNU Affero General Public License (AGPL) as
# #    published by the Free Software Foundation, either version 3 of the
# #    License, or (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU Affero General Public License for more details.
# #
# #    You should have received a copy of the GNU Affero General Public License
# #    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# #
# ###################################################################################
#
# from odoo import models, fields, api, _
# import base64
# import xlrd
# import tempfile
# import binascii
# import io
# import logging
#
# _logger = logging.getLogger(__name__)
# from datetime import datetime, date
# from odoo.exceptions import UserError, ValidationError, RedirectWarning, Warning
# import openpyxl
# from openpyxl import load_workbook
# from io import BytesIO
# import csv
# import subprocess
# # from pyexcel_ods import get_data
# import codecs
#
#
# class OrderLineProduct(models.TransientModel):
#     _name = "order.line.product"
#
#     fastag_product = fields.Binary('Select File')
#     filename = fields.Char('Select File')
#     order_line_form = fields.One2many('fastag.line.form', 'product_line_id',
#                                       string="All Fastags")
#     user_id = fields.Many2one('res.users', string="User",
#                               default=lambda self: self.env.user.id)
#     picking_id = fields.Many2one('stock.picking', "Picking",
#                                  ondelete='cascade')
#
#     def upload_product_line(self):
#         if self.fastag_product == False:
#             raise UserError(
#                 _('Please Upload your excel first then imoport fastag'))
#         else:
#             if not self.filename.endswith('csv'):
#                 raise UserError(
#                     _('Please Upload csv file'))
#             csv_data = base64.b64decode(self.fastag_product)
#             string_data = csv_data.decode('utf-8')
#             data_file = io.StringIO(string_data)
#             data_file.seek(0)
#             file_reader = []
#             try:
#                 csv_reader = csv.reader(data_file, delimiter=',')
#                 next(csv_reader)
#                 file_reader.extend(csv_reader)
#                 data = len(list(file_reader))
#                 picking_id = self.env['stock.picking'].browse(
#                     self._context.get('active_id', False))
#                 today = date.today()
#                 lst_date = str(today).split("-")
#                 today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
#                 terms = []
#                 assigned_id = ''
#                 circle_id = ''
#                 for row_vals in file_reader:
#                     if picking_id:
#                         if assigned_id == '':
#                             login = row_vals[5]
#                             assigned_id = self.env['res.users'].sudo().search(
#                                 [('login', '=', login)])
#                             query1 = """SELECT * FROM rs_circle_name WHERE
#                                                     name = %(circle)s"""
#                             self.env.cr.execute(query1, {
#                                 'circle': str(row_vals[1]),
#                             })
#                             circle_id = self.env.cr.fetchall()
#                             if assigned_id:
#                                 # query1 = """SELECT * FROM rs_circle_name WHERE
#                                 #                                          name = %(circle)s"""
#                                 # self.env.cr.execute(query1, {
#                                 #     'circle': str(row_vals[1]),
#                                 # })
#                                 #
#                                 # circle_id = self.env.cr.fetchall()
#                                 query = """UPDATE stock_picking
#                                                         SET rs_emp_no = %(emp)s,
#                                                             rs_destination_id = %(dest)s,
#                                                             rs_circle_id = %(circle)s,
#                                                             rs_state = 'assign'
#                                                          WHERE id = %(name)s """
#                                 self.env.cr.execute(query,
#                                                     {'emp': int(row_vals[5]),
#                                                      'dest': assigned_id.id,
#                                                      'circle': circle_id[0][
#                                                          0],
#                                                      'name': picking_id.id
#                                                      })
#                                 if assigned_id.rs_designation == 'em':
#                                     listids = []
#                                     for each in assigned_id.rs_circle_ids:
#                                         listids.append(each.id)
#                                     if circle_id[0][0] not in listids:
#                                         raise UserError(
#                                             _('Mismatching circle name'))
#                                 elif assigned_id.rs_circle.id != circle_id[0][
#                                     0]:
#                                     raise UserError(
#                                         _('Mismatching circle name'))
#
#                                 if data > 101 and assigned_id.rs_designation == 'fastag_promoter':
#                                     raise UserError(
#                                         _('You are not allowed to trasfer more then 100 fastag !'))
#
#                                 if assigned_id.rs_designation == 'fastag_promoter':
#                                     records = self.env[
#                                         'product.template'].sudo().search_count(
#                                         [('warehouse_emp_no', '=',
#                                           assigned_id.rs_employee_id)])
#
#                                     fastags_needed = int(records) + data
#                                     if int(records) >= 100:
#                                         raise UserError(
#                                             _('Promoter %s fastag count is exceeds the limit 100',
#                                               assigned_id.name))
#                                     elif int(fastags_needed) > 100:
#                                         raise UserError(
#                                             _('Promoter %s Already there are %s FASTag you can assign %s !',
#                                               assigned_id.name, int(records),
#                                               100 - records))
#
#                                     if assigned_id.rs_designation == 'fastag_tl':
#                                         records = self.env[
#                                             'product.template'].sudo().search_count(
#                                             [('warehouse_emp_no', '=',
#                                               assigned_id.rs_employee_id)])
#
#                                         fastags_needed = int(records) + data
#                                         if int(records) >= 1001:
#                                             raise UserError(
#                                                 _('Team leader %s fastag count is exceeds the limit 1000',
#                                                   assigned_id.name))
#                                         elif int(fastags_needed) >= 1001:
#                                             raise UserError(
#                                                 _('Team leader %s Already there are %s FASTag you can assign %s !',
#                                                   assigned_id.name,
#                                                   int(records),
#                                                   1000 - records))
#
#                                 query = """
#                                          SELECT *
#                                           FROM product_product pp
#                                          LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
#                                              WHERE pp.barcode = %(barcode)s AND pt.warehouse_emp_no = %(emp)s
#                                      AND pt.fastag_sold = 'no' AND pt.rs_faulty_stag = 'no' AND pt.unlink_fastag IS NOT TRUE
#                                  """
#                                 self.env.cr.execute(query,
#                                                     {'barcode': str(
#                                                         row_vals[0]),
#                                                         'emp': self.env.user.rs_employee_id
#                                                     })
#                                 product_ids = self.env.cr.fetchall()
#                                 list_rec = []
#                                 for rec in product_ids:
#                                     list_rec.append(rec[4]
#                                                     )
#                                 if str(row_vals[0]) not in list_rec:
#                                     raise UserError(
#                                         _('%s Barcode is not available in the Products !',
#                                           str(row_vals[0])))
#
#                                 for product_id in product_ids:
#                                     terms.append(
#                                         (0, 0, {'picking_id': picking_id.id,
#                                                 'product_id': product_id[0],
#                                                 'fatag_bracode': str(
#                                                     row_vals[0]),
#                                                 'circle_name': row_vals[1],
#                                                 'date_of_dispatch': today,
#                                                 'consignment_no': str(
#                                                     row_vals[3]),
#                                                 'delivery_partner': row_vals[4],
#                                                 'emp_mobile_no': row_vals[5],
#                                                 'category_id': product_id[24]
#                                                 # 'category_id': int(row_vals[6])
#                                                 }))
#                             else:
#                                 raise UserError(
#                                     _('Please check the assignee mobile number'))
#                 self.sudo().update({'order_line_form': terms})
#                 return {
#                     'name': _('Product Selection'),
#                     'type': 'ir.actions.act_window',
#                     'view_mode': 'form',
#                     'res_model': 'order.line.product',
#                     'view_id': self.env.ref(
#                         'rn_vehical_class.add_product_in_line_form_view').id,
#                     'res_id': self.id,
#                     'target': 'new'
#                 }
#
#             except csv.Error:
#                 raise UserError(
#                     _("Cannot determine the file format for the attached file."))
#
#     def set_fastag_move_details(self):
#         today = date.today()
#         lst_date = str(today).split("-")
#         today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
#         picking_id = self.env['stock.picking'].browse(
#             self._context.get('active_id', False))
#         for line in self.order_line_form:
#             circle_id = self.env['rs.circle.name'].search(
#                 [('name', '=', line.circle_name)])
#             if not circle_id:
#                 raise ValidationError(
#                     _(' Please Create Proper Circle Name %s Is Not Given In The List!',
#                       line.circle_name))
#                 circle_id = self.env['rs.circle.name'].create(
#                     {'name': line.circle_name})
#             stock = self.env['stock.move'].sudo().create({})
#             query1 = """UPDATE stock_move SET product_id=%(product_id)s,
#
#                                               circle_name=%(circle_name)s,
#                                               consignment_no=%(consignment_no)s,
#                                               delivery_partner=%(delivery_partner)s,
#                                               emp_mobile_no=%(emp_mobile_no)s,
#                                               name=%(name)s,
#
#                                                 product_uom=%(product_uom)s,
#                                                 location_id=%(location_id)s,
#                                                 picking_id=%(picking_id)s,
#                                                 location_dest_id=%(location_dest_id)s,
#                                                 category_id=%(category_id)s
#                                                 WHERE id = %(id)s
#                      """
#             self.env.cr.execute(query1,
#                                 {'product_id': line.sudo().product_id.id,
#
#                                  'circle_name': circle_id.id,
#                                  'consignment_no': line.consignment_no,
#                                  'delivery_partner': line.delivery_partner,
#                                  'emp_mobile_no': line.emp_mobile_no,
#                                  'name': line.sudo().product_id.name,
#                                  'product_uom': line.sudo().product_id.uom_id.id,
#                                  'location_id': 24,
#                                  'picking_id': line.picking_id.id,
#                                  'location_dest_id': 24,
#                                  'category_id': line.category_id.id,
#                                  'id': stock.id
#
#                                  })
#
#             query = """UPDATE product_template
#                                                SET warehouse_emp_no = Null,
#                                                product_assigned_to = %(assign)s
#                                                 WHERE id = %(id)s """
#             self.env.cr.execute(query, {
#                 'id': line.sudo().product_id.product_tmpl_id.id,
#                 'assign': line.picking_id.rs_destination_id.id})
#
#         if not self.order_line_form:
#             raise UserError(_('You can not confirm empty fastag !'))
#         template = self.env.ref(
#             'rn_vehical_class.inventory_trasfer_assigned_email_template')
#         print("======", template.email_to, self.id)
#         self.env['mail.template'].browse(template.id).send_mail(
#             self.order_line_form[0].picking_id.id)
#
#         return True
#
#
# class MessageWizard(models.TransientModel):
#     _name = 'message.wizard'
#
#     message = fields.Char('Message', readonly=True, required=True)
#
#     # @api.multi
#     def action_ok(self):
#         """ close wizard"""
#         return {'type': 'ir.actions.act_window_close'}
#
#
# class FastagLineForm(models.TransientModel):
#     _name = 'fastag.line.form'
#
#     product_line_id = fields.Many2one('order.line.product', string="Order Line")
#     product_id = fields.Many2one('product.product', string="Products",
#                                  store=True)
#     picking_id = fields.Many2one('stock.picking', "Picking",
#                                  required=True, ondelete='cascade')
#     fatag_bracode = fields.Char(string="FASTAG BARCODE")
#     circle_name = fields.Char(string="CIRCLE NAME")
#     date_of_dispatch = fields.Char(string="DATE OF DISPATCH")
#     consignment_no = fields.Char(string="CONSIGNMENT NO")
#     delivery_partner = fields.Char(string="DELIVERY PARTNER")
#     emp_mobile_no = fields.Char(string="EMP MOB NO")
#     category_id = fields.Many2one('product.category', string="TAG CLASS")
