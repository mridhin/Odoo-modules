from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_studio_doc = fields.Char('Doc No.')
