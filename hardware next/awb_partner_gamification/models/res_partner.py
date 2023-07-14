from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_credit_limit = fields.Monetary(string='Credit Limit', compute='_compute_credit_limit_compute',
        currency_field='currency_id', help='Partners Available Credit Limit.')

    @api.depends_context('company')
    def _compute_credit_limit_compute(self):
        for partner in self:
            partner_credit_limit = partner.credit
            partner.update({
                'partner_credit_limit': partner_credit_limit
            })
