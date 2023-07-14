# -*- coding: utf-8 -*-

#  import from odoo lib
from odoo import fields, models

"""Inherited model pos.config to add field."""
class PosConfigInherited(models.Model):
    _inherit = 'pos.config'
    _description = 'Point of Sale Configuration'


    awb_customer_offline = fields.Boolean(string="Customer Offline", copy=False, readonly=False,translate=False, index=False)