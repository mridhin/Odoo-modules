from odoo import models, fields, api


class HotelRoom(models.Model):
    _name = 'hotel.room'

    name = fields.Integer(default="100", string='Room No')
    beds = fields.Selection([('single', 'Single'), ('dormitory', 'Dormitory'),
                             ('double', 'Double')], string='Bed')
    available_seats = fields.Integer(string='Available seats')
    facility_ids = fields.Many2many('hotel.facility', string='Facility')
    rent = fields.Integer(default='100', string='Rent/Day')
    currency_id = fields.Many2one('res.currency', string='Currency')
    accommodation = fields.One2many('hotel.booking', 'room_id',
                                    string='Accommodation')
    state = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available')], readonly=True, default='available',
        string='State')
    #state = fields.Selection(related="accommodation.state")
    guest_name = fields.Many2one(related='accommodation.partner_id')







