# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    awb_vat_registration_status = fields.Selection([
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('vat_Exempt', 'VATExempt'),
    ], default='unregistered', string="VAT Registration Status")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            self.awb_vat_registration_status = self.partner_id.awb_vat_registration_status
        else:
            self.awb_vat_registration_status = 'unregistered'


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('tax_id')
    def _onchange_discount(self):
        super(SaleOrderLine, self)._onchange_discount()
        if len(self.tax_id) > 1:
            raise UserError(
                ("You cannot enter more than one tax"))
