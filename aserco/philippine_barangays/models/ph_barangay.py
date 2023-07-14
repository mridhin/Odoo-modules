from odoo import api, fields, models


class CityBarangay(models.Model):
    _name = 'res.city.barangay'
    _description = 'City Barangay'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(string="Barangay")
    brgy_code = fields.Char(string="Barangay Code")
    active = fields.Boolean(string="Active", default=True)
    city_id = fields.Many2one('res.state.city', string="City/Municipality")
    state_id = fields.Many2one('res.country.state', string="State/Province", related='city_id.state_id', store=True)

    @api.model
    def create(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].title()
        return super(CityBarangay, self).create(vals)

    def write(self, vals):
        if 'name' in vals:
            if vals.get('name'):
                vals['name'] = vals['name'].title()
        return super(CityBarangay, self).write(vals)