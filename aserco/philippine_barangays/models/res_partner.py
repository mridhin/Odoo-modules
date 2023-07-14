from odoo import fields, models, api, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_city_id = fields.Many2one('res.state.city',string="City/Municipality",domain="[('state_id','=?',state_id)]")
    city_id = fields.Many2one('res.state.city',related="partner_city_id", string="City/Municipality")
    country_code = fields.Char(related='country_id.code',string="Country Code")
    barangay_id = fields.Many2one('res.city.barangay', string="Barangay", domain="[('city_id','=?',partner_city_id)]")

    @api.onchange('partner_city_id')
    def onchange_city_id(self):
        self.city = self.partner_city_id.name

    @api.onchange('city_id')
    def _onchange_city_id(self):
        return

    @api.model
    def create(self, values):
        result = super(ResPartner, self).create(values)
        if values.get('partner_city_id'):
            city = self.env['res.state.city'].browse(values['partner_city_id'])
            result['partner_city_id'] = city.name
        return result
