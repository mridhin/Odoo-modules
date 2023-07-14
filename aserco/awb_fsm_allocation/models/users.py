from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'
    _order = 'priority_asc desc'

    priority_asc = fields.Boolean(related='partner_id.priority_asc', store=True)
