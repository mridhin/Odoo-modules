# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import xlrd
import tempfile
import binascii
import io
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError, RedirectWarning, Warning
import openpyxl
from openpyxl import load_workbook
from io import BytesIO
import csv
import subprocess
from pyexcel_ods import get_data
import codecs
import collections


class unlinked_tag(models.Model):
    _name = 'unlinked_tag.unlinked_tag'
    _description = 'unlinked_tag'

    name = fields.Char(string='Txn date')
    month = fields.Char(string="Month")
    tag_id = fields.Char(string='Tag ID')
    bar_code = fields.Char(string='Barcode No')
    amount = fields.Float(string='Amount')
    toll_plaza = fields.Char(string='Toll Plaza')
    circle_id = fields.Many2one('rs.circle.name', string="Circle")
    product_assign_to = fields.Many2one('res.users', string="Product Assign To")
    employee_id = fields.Char(string="Employee ID")
    flag = fields.Boolean(string='Flag', default=False)
    product_unlink_by = fields.Many2one('res.users', string="Product Unlink By")
    matched_unlink_record = fields.Selection(
        [('matched', 'Matched'), (' ', 'Un Matched')],
        default=' ', string="Matched")
    matched = fields.Char(string="Matched")
    unmatched = fields.Char(string="Mismatched")

    def update_unlink_circle(self):
        unlink_obj = self.search([('circle_id', '=', False),('matched', '!=', False)])
        print(unlink_obj)
        for rec in unlink_obj:
            moveline_product = self.env['stock.move'].search([('fatag_bracode', '=', rec.bar_code)], limit=1)
            print(moveline_product)
            if moveline_product:
                for move in moveline_product:
                    rec.circle_id = move.circle_name.id


class CheckWizard(models.TransientModel):
    _name = 'check.wizard'

    unlink_product = fields.Binary('Select File')
    filename = fields.Char('Select File')
    unlinked_maching_ids = fields.One2many('unlinked.matching',
                                           'unlinked_tag_id',
                                           )
    unlinked_mismaching_ids = fields.One2many('unlinked.mismatching',
                                              'unlinked_tag_id',
                                              )
    unlink_ids = fields.One2many('unlinked.sheet',
                                 'unlinked_tag_id')
    duplicate_ids = fields.One2many('unlinked.duplicate',
                                    'unlinked_tag_id')

    def upload_file(self):
        if self.unlink_product == False:
            raise UserError(
                _('Please upload your file'))
        csv_data = base64.b64decode(self.unlink_product)
        string_data = csv_data.decode('utf-8')
        data_file = io.StringIO(string_data)
        data_file.seek(0)
        file_reader = []
        try:
            csv_reader = csv.reader(data_file, delimiter=',')
            if not len(next(csv_reader)) == 5:
                raise UserError('Please check columns in your sheet')
            file_reader.extend(csv_reader)
            data = len(list(file_reader))
            count = collections.Counter()
            list1 = []
            list2 = []
            sheet_list = []
            sheet_duplicate_list = []
            internal_ref = []
            for row_vals in file_reader:
                sheet_list.append(
                    (0, 0, {'name1': row_vals[0],
                            'month': row_vals[1],
                            'tag_id': row_vals[2],
                            # 'bar_code': product_id[0][0],
                            'amount': row_vals[3],
                            'toll_plaza': row_vals[4],
                            }))
            self.write({'unlink_ids': sheet_list})
            self.sudo().env.cr.execute("""INSERT INTO unlinked_matching ( name1, month,tag_id,bar_code,
            amount,toll_plaza,circle_id,product_assign_to,employee_id,unlinked_tag_id)
            SELECT us.name1, us.month,us.tag_id,pp.barcode,us.amount,us.toll_plaza,st.circle_name,
            pt.product_assigned_to,rs.rs_employee_id,us.unlinked_tag_id
            FROM unlinked_sheet us INNER JOIN product_template pt ON us.tag_id = pt.default_code
            INNER JOIN res_users rs ON pt.product_assigned_to = rs.id
            INNER JOIN product_product pp ON pt.id = pp.product_tmpl_id
            INNER JOIN stock_move st ON st.fatag_bracode = pp.barcode and st.id = (select max(id) from stock_move where fatag_bracode = pp.barcode)
             WHERE us.unlinked_tag_id = %s""" % (self.id))
            self.sudo().env.cr.execute("""INSERT INTO unlinked_mismatching ( name1, month,tag_id,amount,toll_plaza,unlinked_tag_id)
            SELECT us.name1, us.month,us.tag_id,us.amount,us.toll_plaza,us.unlinked_tag_id
            FROM unlinked_sheet us
             WHERE us.unlinked_tag_id = %s and us.tag_id NOT IN (SELECT tag_id FROM unlinked_matching WHERE unlinked_tag_id = %s )
            """ % (self.id, self.id))

            # return a wizard that show both matched and unmatched records
            return {
                'name': _('Unlink Tag'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'check.wizard',
                'view_id': self.env.ref(
                    'unlinked_tag.check_wizard_form').id,
                'res_id': self.id,
                'target': 'new'
            }
        except csv.Error:
            raise UserError(
                _("Cannot determine the file format for the attached file."))

    def accept(self):

        self.sudo().env.cr.execute("""INSERT INTO unlinked_tag_unlinked_tag( name, month,tag_id,bar_code,
                    amount,toll_plaza,circle_id,matched) 
                    SELECT um.name1, um.month,um.tag_id,pp.barcode,um.amount,um.toll_plaza,um.circle_id,um.name1
                    FROM unlinked_matching um INNER JOIN product_template pt ON um.tag_id = pt.default_code 
                    INNER JOIN product_product pp ON pt.id = pp.product_tmpl_id
                     WHERE um.unlinked_tag_id = %s """ % (self.id))

        update_product_query = """UPDATE product_template pt SET unlink_fastag = %(unlink_fastag)s,
                        unlink_amount =
                        CASE
                        WHEN unlink_amount >0 THEN
                            CASE
                                WHEN (SELECT count(amount) FROM unlinked_matching WHERE tag_id = pt.default_code and unlinked_tag_id = %(id1)s) >0 
                            THEN
                            unlink_amount + (SELECT sum(amount)  FROM unlinked_matching WHERE tag_id = pt.default_code and unlinked_tag_id = %(id1)s)
                            ELSE
                            unlink_amount + (SELECT amount FROM unlinked_matching WHERE tag_id = pt.default_code and unlinked_tag_id = %(id1)s)
                            END 
                        ELSE
                            CASE
                                WHEN (SELECT count(amount) FROM unlinked_matching WHERE tag_id = pt.default_code and unlinked_tag_id = %(id1)s) >0 
                            THEN
                            (SELECT sum(amount)  FROM unlinked_matching WHERE tag_id = pt.default_code and unlinked_tag_id = %(id1)s)
                            ELSE
                            (SELECT amount FROM unlinked_matching WHERE tag_id = pt.default_code and unlinked_tag_id = %(id1)s)
                            END 
                        END
                        WHERE default_code IN (SELECT tag_id FROM unlinked_matching WHERE unlinked_tag_id = %(id1)s)"""
        self.env.cr.execute(update_product_query,
                            {'id1': self.id, 'unlink_fastag': True})
        self.sudo().env.cr.execute("""INSERT INTO unlinked_report( name, month,tag_id,bar_code,
                    amount,toll_plaza,circle_id,product_assign_to,employee_id) 
                    SELECT um.name1, um.month,um.tag_id,pp.barcode,um.amount,um.toll_plaza,um.circle_id,
                    pt.product_assigned_to,um.employee_id
                    FROM unlinked_matching um INNER JOIN product_template pt ON um.tag_id = pt.default_code 
                    INNER JOIN product_product pp ON pt.id = pp.product_tmpl_id
                     WHERE um.unlinked_tag_id = %s""" % (self.id))

        self.sudo().env.cr.execute("""INSERT INTO unlinked_tag_unlinked_tag( name, month,tag_id,
                            amount,toll_plaza,unmatched) 
                            SELECT umi.name1, umi.month,umi.tag_id,umi.amount,umi.toll_plaza,umi.name1
                            FROM unlinked_mismatching umi 
                             WHERE umi.unlinked_tag_id = %s""" % (self.id))

        stock_move_update_query = """UPDATE stock_move
                                                       SET unlink_fastag = %(unlink)s
                                                        WHERE fatag_bracode IN (SELECT bar_code FROM unlinked_matching
                                                           WHERE unlinked_tag_id = %(id)s) """
        self.sudo().env.cr.execute(stock_move_update_query, {'id': self.id,
                                                             'unlink': True
                                                             })
        update_transfer_query = """UPDATE all_transfer_report ap SET rs_unlinked = %(unlink_fastag)s,
                        product_amount =
                        CASE
                        WHEN product_amount >0 THEN
                            CASE
                                WHEN (SELECT count(amount) FROM unlinked_matching WHERE bar_code = ap.name and unlinked_tag_id = %(id1)s) >0 
                            THEN
                            product_amount + (SELECT sum(amount)  FROM unlinked_matching WHERE bar_code = ap.name and unlinked_tag_id = %(id1)s)
                            ELSE
                            product_amount + (SELECT amount FROM unlinked_matching WHERE bar_code = ap.name and unlinked_tag_id = %(id1)s)
                            END 
                        ELSE
                            CASE
                                WHEN (SELECT count(amount) FROM unlinked_matching WHERE bar_code = ap.name and unlinked_tag_id = %(id1)s) >0 
                            THEN
                            (SELECT sum(amount)  FROM unlinked_matching WHERE bar_code = ap.name and unlinked_tag_id = %(id1)s)
                            ELSE
                            (SELECT amount FROM unlinked_matching WHERE bar_code = ap.name and unlinked_tag_id = %(id1)s)
                            END 
                        END
                        WHERE name IN (SELECT bar_code FROM unlinked_matching WHERE unlinked_tag_id = %(id1)s)"""
        self.env.cr.execute(update_transfer_query,
                            {'id1': self.id, 'unlink_fastag': True})

    def dontaccept(self):
        print('cancel')


class unlinked_tag_maching(models.TransientModel):
    _name = 'unlinked.matching'
    _description = 'unlinked match record'

    unlinked_tag_id = fields.Many2one('check.wizard')
    name1 = fields.Char(string='Txn date')
    month = fields.Char(string="Month")
    tag_id = fields.Char(string='Tag ID')
    bar_code = fields.Char(string='Barcode No')
    amount = fields.Float(string='Amount')
    toll_plaza = fields.Char(string='Toll Plaza')
    circle_id = fields.Many2one('rs.circle.name', string="Circle")
    product_assign_to = fields.Many2one('res.users', string="Product Assign To")
    employee_id = fields.Char(string="Employee ID")
    flag = fields.Boolean(string='Flag', default=True)
    matched = fields.Char(string="Matched")
    # matched = fields.Boolean(string="Matched")


class unlinked_tag_mismaching(models.TransientModel):
    _name = 'unlinked.mismatching'
    _description = 'unlinked mismatch record'

    unlinked_tag_id = fields.Many2one('check.wizard')
    name1 = fields.Char(string='Txn date')
    month = fields.Char(string="Month")
    tag_id = fields.Char(string='Tag ID')
    bar_code = fields.Char(string='Barcode No')
    amount = fields.Float(string='Amount')
    toll_plaza = fields.Char(string='Toll Plaza')
    circle_id = fields.Many2one('rs.circle.name', string="Circle")
    flag = fields.Boolean(string='Flag', default=False)


class unlinked_tag_sheet(models.TransientModel):
    _name = 'unlinked.sheet'
    _description = 'unlinked sheet record'

    unlinked_tag_id = fields.Many2one('check.wizard')
    name1 = fields.Char(string='Txn date')
    month = fields.Char(string="Month")
    tag_id = fields.Char(string='Tag ID')
    bar_code = fields.Char(string='Barcode No')
    amount = fields.Float(string='Amount')
    toll_plaza = fields.Char(string='Toll Plaza')
    circle_id = fields.Many2one('rs.circle.name', string="Circle")
    flag = fields.Boolean(string='Flag', default=False)


class unlinked_tag_duplicatet(models.TransientModel):
    _name = 'unlinked.duplicate'
    _description = 'unlinked duplicate record'

    unlinked_tag_id = fields.Many2one('check.wizard')
    name1 = fields.Char(string='Txn date')
    month = fields.Char(string="Month")
    tag_id = fields.Char(string='Tag ID')
    bar_code = fields.Char(string='Barcode No')
    amount = fields.Float(string='Amount')
    toll_plaza = fields.Char(string='Toll Plaza')
    circle_id = fields.Many2one('rs.circle.name', string="Circle")
    flag = fields.Boolean(string='Flag', default=False)
    matched = fields.Char(string="Matched")
