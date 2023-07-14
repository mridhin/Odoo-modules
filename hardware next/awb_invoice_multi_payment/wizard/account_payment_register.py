from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_create_draft_payment = fields.Boolean(string="Create Draft Payment", default=False)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['is_create_draft_payment'] = self._context.get('is_create_draft_payment',False)
        return res

    def _create_draft_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            to_process.append({
                'create_vals': payment_vals,
                'to_reconcile': batches[0]['lines'],
                'batch': batches[0],
            })
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'payment_values': {
                                **batch_result['payment_values'],
                                'payment_type': 'inbound' if line.balance > 0 else 'outbound'
                            },
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        return payments

    def action_create_payments(self):
        if self.is_create_draft_payment:
            payments = self._create_draft_payments()
        else:
            payments = self._create_payments()

        # If change status to "CR Sent" once Countered receipt payment is created.
        if self._context.get('active_ids'):
            for active in self._context.get('active_ids'):
                account_move_id = self.env['account.move'].sudo().search([('id', '=',int(active))])
                account_move_id.payment_state = 'cr_sent'
                account_move_id.payment_id = payments

        if self._context.get('dont_redirect_to_payments'):
            return True
        
        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        # If once click create payment button then automatically sequence number generated in payment table(CTR Receipt status)
        if len(payments) == 1:
            payments.action_for_ctr_receipt()
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            payments.action_for_ctr_receipt()
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        
        return action
    #should be redirect users to payment directly on countered receipt status
    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'state':'ctr_receipt'
        }) 
        return result
    
    #The check group payment by default if multiple invoices were selected
    @api.depends('can_edit_wizard')
    def _compute_group_payment(self):
        for wizard in self:
            
            if wizard.can_edit_wizard:
                batches = wizard._get_batches()
                wizard.group_payment = len(batches[0]['lines'].move_id) == 1
                if wizard.can_group_payments == True:
                    wizard.group_payment = 'true'
            else:
                wizard.group_payment = False