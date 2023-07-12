# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import csv
import io
from datetime import datetime, date

class ProductImport(models.Model):
    _inherit = "product.product"


class import_button(models.Model):
    _inherit = "product.template"

    uom_id = fields.Many2one(required=False)
    uom_po_id = fields.Many2one(required=False)
    tracking = fields.Selection(required=False)
    name = fields.Char(required=False)



    def import_product(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Fastag',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'import.product',
            'target': 'new',
        }

class ImportProduct(models.TransientModel):
    _name = "import.product"

    fastag_product = fields.Binary('Select File')
    filename = fields.Char('Select File')
    import_line_form = fields.One2many('import.product.line', 'import_id',
                                      string="All Fastags")

    def import_product_line(self):
        if self.fastag_product == False:
            raise UserError('Please Upload your csv first then imoport fastag')
        else:
            if not self.filename.endswith('csv'):
                raise UserError('Please Upload csv file')
            csv_data = base64.b64decode(self.fastag_product)
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
                if data > 10000:
                    raise UserError('Cant import fastag more than 10000')
                today = date.today()
                # lst_date = str(today).split("-")
                # today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
                categ_id = ""
                tag_color_id = ""
                partner_id = ""
                user_id = ""
                index = 1
                for row_vals in file_reader:
                    index += 1
                    if categ_id == "" and partner_id == "" and user_id == "" and tag_color_id == "":
                        categ_id = self.env['product.category'].sudo().search(
                                [('name', '=', row_vals[4])])
                        if not categ_id:
                            raise UserError(
                                                _('%s category is not available',
                                                  row_vals[4]))
                        tag_color_id = self.env['res.partner.category'].sudo().search(
                                [('name', '=', row_vals[6])])
                        if not tag_color_id:
                            raise UserError(
                                                _('%s tag color is not available',
                                                  row_vals[6]))
                        partner_id = self.env['res.partner'].search(
                                [('name', '=', row_vals[7])])
                        if not partner_id:
                            raise UserError(
                                _('%s vender is not available',
                                  row_vals[7]))

                        user_id = self.env['res.users'].search([('rs_employee_id','=',row_vals[9])])
                        if not user_id:
                            raise UserError(
                                _(' User with %s employee id is not available',
                                  row_vals[9]))
                    if not categ_id.name == row_vals[4]:
                        categ_id = self.env['product.category'].sudo().search(
                            [('name', '=', row_vals[4])])
                        if not categ_id:
                            raise UserError(
                                                _('%s category is not available',
                                                  row_vals[4]))
                    if not partner_id.name == row_vals[7]:
                        partner_id = self.env['res.partner'].search(
                            [('name', '=', row_vals[7])])
                        if not partner_id:
                            raise UserError(
                                _('%s vender is not available',
                                  row_vals[7]))
                    if not tag_color_id.name == row_vals[6]:
                        tag_color_id = self.env[
                            'res.partner.category'].sudo().search(
                            [('name', '=', row_vals[6])])
                        if not tag_color_id:
                            raise UserError(
                                _('%s tag color is not available',
                                  row_vals[6]))

                    if user_id.rs_employee_id == row_vals[9]:
                        terms.append(
                            (0, 0, {'barcode': row_vals[0],
                                    'tag_id': row_vals[1],
                                    'vendor_id': row_vals[2],
                                    'inward_date': today,
                                    'categ_id': categ_id.id,
                                    'vehicle_type_id': row_vals[5],
                                    'tag_color': tag_color_id.id,
                                    'partner_id': partner_id.id,
                                    'name': row_vals[8],
                                    'employee_id': row_vals[9]
                                    }))

                    else:
                        raise UserError(
                            _('Please check the values in line number %s',
                              index))
                self.sudo().update({'import_line_form': terms})
                return {
                    'name': _('Import Fastag'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.product',
                    'view_id': self.env.ref(
                        'import_button.add_product_action_view').id,
                    'res_id': self.id,
                    'target': 'new'
                }

            except csv.Error:
                raise UserError("Cannot determine the file format for the attached file.")

    def import_fastag(self):
        insert_fastag_records = []
        # query = """SELECT product_tmpl_id FROM product_product order by "id" desc limit 1"""
        # self.env.cr.execute(query)
        # product_last = self.env.cr.fetchall()
        # product_last_id = sum(product_last[0])
        # print(product_last_id)
        # product_tmpl_id = int(product_last_id) + 1
        for product_id in self.import_line_form:
            # product = self.env['product.template'].create({'barcode': product_id.barcode})
            product_insert_values = {
                # 'barcode': product_id.barcode,
                                    'default_code': product_id.tag_id,
                                    'rs_vendor_name': product_id.vendor_id,
                                   'inword_date': product_id.inward_date,
                                    'categ_id': product_id.categ_id.id,
                                    'rs_tag_id': product_id.vehicle_type_id,
                                    # 'tag_color': product_id.tag_color.id,
                                    'partner_id': product_id.partner_id.id,
                                    'name': product_id.name,
                                    'warehouse_emp_no': product_id.employee_id,
                                   # 'product_tmpl_id': product_tmpl_id,
                                    #'id': product_tmpl_id,
                                    # 'id':product.id,
                                    #'idp':product.id
                                    'type':'product',
                                    'active': 'true',
                                    'rs_faulty_stag':'no',
                'fastag_sold':'no',
                'uom_id':1,
                'uom_po_id':1
                                    }

            #insert_fastag_records.append(product_insert_values)
            #product_tmpl_id += product_tmpl_id
        # product_template_query = """
        #
        #                                                 UPDATE product_template
        #
        #                                               SET
        #
        #                                               categ_id=%(categ_id)s,
        #                                               rs_tag_id=%(rs_tag_id)s,
        #
        #                                                 name=%(name)s,
        #                                                 warehouse_emp_no=%(warehouse_emp_no)s
        #                                                 WHERE id = %(id)s
        #                      """
        # self.env.cr.executemany(product_template_query, insert_fastag_records)
        # product_product_query = """UPDATE product_product SET barcode=%(barcode)s
        #                                                         WHERE id = %(idp)s
        #                              """
        # self.sudo().env.cr.executemany(product_product_query, insert_fastag_records)
#
        #self.env['product.product'].create(insert_fastag_records)
            insert_product_temp_sql = """INSERT INTO product_template ( default_code, rs_vendor_name,inword_date, categ_id, rs_tag_id, partner_id, name,type,
                                                       warehouse_emp_no,active,rs_faulty_stag,fastag_sold,uom_id,uom_po_id) VALUES (%(default_code)s,
                                                        %(rs_vendor_name)s, %(inword_date)s, %(categ_id)s, %(rs_tag_id)s,
                                                        %(partner_id)s, %(name)s, %(type)s,%(warehouse_emp_no)s,%(active)s,%(rs_faulty_stag)s,
                                                        %(fastag_sold)s,%(uom_id)s,%(uom_po_id)s) RETURNING id"""

            self.env.cr.execute(insert_product_temp_sql,
                                    product_insert_values)
            templateid = self.env.cr.fetchone()
            print(templateid)
            # templateid = sum(templateid)
            insert_fastag_sql = """INSERT INTO product_product ( barcode,product_tmpl_id,active,default_code)
             VALUES (%(barcode)s,%(temp)s,%(active)s,%(default_code)s)"""
            self.env.cr.execute(insert_fastag_sql,
                                {'barcode': product_id.barcode,
                                 'temp':templateid,'active':'true','default_code':product_id.tag_id})

            insert_tag_color_sql = """INSERT INTO product_id ( product_template_id, res_partner_category_id )
             VALUES (%(temp)s,%(tag)s)"""

            self.env.cr.execute(insert_tag_color_sql,
                                {
                                 'temp': templateid,
                                 'tag': product_id.tag_color.id})


class ImportProductLine(models.TransientModel):
    _name = "import.product.line"

    barcode = fields.Char(string="Barcode")
    tag_id = fields.Char(string="Tag ID")
    vendor_id = fields.Char(string="Vendor ID")
    inward_date = fields.Date(string="Inward Date")
    categ_id = fields.Many2one('product.category',string="Vehicle Type")
    vehicle_type_id = fields.Char(string="Vehicle Type ID")
    tag_color = fields.Many2one('res.partner.category',string="Tag Color")
    partner_id = fields.Many2one('res.partner',string="Vender Name")
    name = fields.Char(string="Product Name")
    employee_id = fields.Char(string="Employee ID")
    import_id = fields.Many2one('import.product')