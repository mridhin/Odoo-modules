from odoo import api, fields, models


class CountryState(models.Model):
    _inherit = 'res.country.state'
    _description = "Country state"

    city_ids = fields.One2many('res.state.city', 'state_id', string="City/Municipality")
    country_code = fields.Char(related='country_id.code', store=True)


class StateCity(models.Model):
    _name = 'res.state.city'
    _description = 'State City'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(string="City/Municipality")
    city_code = fields.Char(string="City/Municipality Code")
    active = fields.Boolean(string="Active", default=True)
    state_id = fields.Many2one('res.country.state', string="Province")
    brgy_ids = fields.One2many('res.city.barangay', 'city_id', string="Barangays")

    @api.model
    def create(self, vals):
        if vals['name']:
            vals['name'] = vals['name'].title()
        return super(StateCity, self).create(vals)

    def write(self, vals):
        if 'name' in vals:
            if vals['name']:
               vals['name'] = vals['name'].title()
        return super(StateCity, self).write(vals)
