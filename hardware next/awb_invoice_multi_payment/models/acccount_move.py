from odoo import models, fields, api, _
from odoo.exceptions import UserError

#Added status "CR Sent" in payment_state
PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Not Paid'),
        ('cr_sent', 'CR Sent'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'), 
        ('invoicing_legacy', 'Invoicing App Legacy'),
]
class AccountMove(models.Model):
    _inherit = "account.move"

    payment_state = fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status", store=True,
                                     readonly=True, copy=False, tracking=True, compute='_compute_amount')
    def action_draft_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        if self.filtered(lambda x: x.partner_id != self[0].partner_id)\
            or self.filtered(lambda x: x.state != "posted")\
            or self.filtered(lambda x: x.payment_state != "not_paid"):
            # or self.filtered(lambda x: x.state == "posted") and\
            # self.filtered(lambda x: x.payment_state == "not_paid"):

            raise UserError(_("Cannot draft Payment due to either of the following errors/s:"
                              "\n- Selected Invoices should be under the same partner"
                              "\n- Selected Invoices payment status should be 'Not paid'"
                              "\n- Selected Invoices status should be posted"))
      
        return {
            'name': _('Draft Payment (Countered Receipt)'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                'is_create_draft_payment': True,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
