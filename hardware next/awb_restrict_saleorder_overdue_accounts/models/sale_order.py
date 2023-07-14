# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        account_id  = self.env['account.move'].search(['|', ('partner_id', '=', self.partner_id.id), ('partner_id.parent_id', '=', self.partner_id.id),  ('payment_state', '!=', 'paid'), ('state', '!=', 'cancel'), ('move_type', '=', 'out_invoice')])
        if account_id:
            raise ValidationError(_("Customer has Overdue Accounts. \n Transaction not allowed!"))
        else:
            return result
