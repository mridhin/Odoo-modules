from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'priority_asc desc'

    priority_asc = fields.Boolean('Priority ASC', groups="base.group_system")
    asc_service_provider = fields.Boolean('Accredited Service Provider', groups="base.group_system")
