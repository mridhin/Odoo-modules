from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_name = fields.Char(String="Pos Name",store=True)
    pos_version = fields.Char(string="Pos Version",store=True)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pos_name', self.pos_name)
        self.env['ir.config_parameter'].sudo().set_param('pos_version', self.pos_version)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            pos_name=ICPSudo.get_param('pos_name'),
            pos_version=ICPSudo.get_param('pos_version'),
        )
        return res