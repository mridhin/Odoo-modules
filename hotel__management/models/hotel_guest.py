from odoo import models, fields, api


class HotelGuest(models.Model):
    _name = 'hotel.guests'

    name = fields.Char(string="Guest")
    address_line1 = fields.Char()
    address_line2 = fields.Char()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")
    age = fields.Integer(string="Age")
    booking_id = fields.Many2one('hotel.booking', string='Bookings')