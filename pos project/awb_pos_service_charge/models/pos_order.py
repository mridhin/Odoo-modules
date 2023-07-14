# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    is_service_percentage = fields.Boolean(string="Is Percentage?")
    service_percentage = fields.Float(string='Service Percentage (%)', digits=0, default=0.0)
    service_amount = fields.Float(string='Service Charge Amount', digits=0, default=0.0)
