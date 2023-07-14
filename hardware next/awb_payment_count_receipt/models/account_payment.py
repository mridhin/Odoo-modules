# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#  import from python lib
from collections import defaultdict

#  import from odoo lib
from odoo import models, fields, api
from odoo.exceptions import ValidationError

#Inherited and added new field for payment table
class InheritedAccountMove(models.Model):
    _inherit = "account.move"
    
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ("ctr_receipt", "CTR Receipt"),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    ctr_reference = fields.Char(string='CTR Reference:', copy=False, tracking=True, readonly=True)
    ctr_reference_name = fields.Char('CTR Reference')
    
class InheritedAccountPayment(models.Model):
    _inherit = "account.payment"
    
    
    #CTR Receipt button action for payment table
    @api.depends('state')
    def action_for_ctr_receipt(self):
        #auto generate sequence number for CTR status
        if self.ctr_reference_name == False:
            self.ctr_reference_name = self.env['ir.sequence'].next_by_code('account.payment.seq')
            self.ctr_reference = self.ctr_reference_name
        self.state = 'ctr_receipt'
