from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    draft_payment_invoice_count = fields.Integer(string="Invoices",
                                                 compute="_compute_invoice_draft_payment")
    draft_payment_invoice_ids = fields.Many2many('account.move', string="Invoices",
                                                 compute="_compute_invoice_draft_payment")

    def _compute_invoice_draft_payment(self):
        self.draft_payment_invoice_count = 0
        invoices = self.env['account.move'].search([('payment_id','=',self.id),('move_type','=','out_invoice')])
        self.draft_payment_invoice_count = len(invoices)
        self.draft_payment_invoice_ids = invoices

    def button_open_draft_payment_invoices(self):
        ''' Redirect the user to the invoice(s) paid by this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Paid Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.reconciled_invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.reconciled_invoice_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.draft_payment_invoice_ids.ids)],
            })
        return action
