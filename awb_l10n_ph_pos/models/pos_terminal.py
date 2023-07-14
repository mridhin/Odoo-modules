from odoo import api, fields, models

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    taxpayer_min = fields.Char(string='Taxpayer Minimum')
    taxpayer_machine_serial_number = fields.Char(string='Taxpayer Machine Serial Number')
    awb_pos_provider_ptu = fields.Char(string='AWB POS Provider PTU')
    crm_team_id = fields.Many2one('crm.team', string='CRM Team')

class PosSession(models.Model):
    _inherit = 'pos.session'

    taxpayer_min = fields.Char(related='config_id.taxpayer_min', store=True)
    taxpayer_machine_serial_number = fields.Char(related='config_id.taxpayer_machine_serial_number',
                                                 store=True)
    awb_pos_provider_ptu = fields.Char(related='config_id.awb_pos_provider_ptu', store=True)



