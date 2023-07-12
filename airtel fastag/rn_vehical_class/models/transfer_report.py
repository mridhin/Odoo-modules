# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.osv import expression
from odoo.exceptions import ValidationError, Warning, UserError
from datetime import datetime


class TaransferReport(models.Model):
    _name = 'transfer.report'
    _description = 'Transfer Report'

    name = fields.Char(string="Barcode No")
    rs_date_dispatch = fields.Char(string="Date Of Dispatch")
    rs_date_transfer = fields.Char(string="Date Of Transfer")
    rs_from_emp_no = fields.Char(string="From EMP No")
    rs_to_emp_no = fields.Char(string="To EMP No")
    parent_id = fields.Many2one("transfer.report", "Parent Department", select=True)
    child_ids = fields.One2many("transfer.report", "parent_id", string="Children")
    assigned_id = fields.Many2one('res.users', copy=False, tracking=True,
        string='Assigned To',
        )
    tag_class = fields.Many2one('product.category', string='Tag Class')

