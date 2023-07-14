from odoo import fields, models, api


class LazadaPaymentMethod(models.Model):
    _name = 'lazada.payment.method'
    _description = 'Lazada Payment Methods'

    name = fields.Char('Payment Method', required=True)
    journal_id = fields.Many2one('account.journal',string='Journal')
