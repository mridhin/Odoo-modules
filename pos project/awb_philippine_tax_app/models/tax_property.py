# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class TaxProperty(models.Model):
    _name = "tax.property"
    _description = "Tax Property"
    _rec_name = 'awb_tax_property_name'
    _order = 'awb_tax_property_name asc'

    awb_tax_property_name = fields.Char('Name')
    awb_tax_property_description = fields.Text('Description')
    awb_type = fields.Selection(
        [('vat', 'VAT'),('ewt', 'EWT')], string="Type")
    active = fields.Boolean(default=True)
