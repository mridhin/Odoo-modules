from odoo import models, fields, api


class HotelFacility(models.Model):
    _name = 'hotel.facility'

    name = fields.Char(string="Facility")
    rent = fields.Integer(string='Rent')