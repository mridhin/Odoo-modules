from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HotelBooking(models.Model):
    _name = "hotel.booking"
    _inherit = ['mail.thread']
    _order = "check_in desc"

    partner_id = fields.Many2one('res.partner', string='Guest')
    check_in = fields.Datetime(string='Check In', default=fields.Datetime.now())
    check_out = fields.Datetime(string='Check Out', default=fields.Datetime.now())
    bed_type = fields.Selection([('single', 'Single'), ('dormitory', 'Dormitory'),
                                 ('double', 'Double')], string='Bed')
    facility_ids = fields.Many2many('hotel.facility', string='Facility')
    room_id = fields.Many2one("hotel.room", string='Room')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel')], readonly=True, default='draft', string='State')
    name = fields.Char(string="Sequence Number", readonly=True, required=True,
                       copy=False, default='NEW')
    expected_days = fields.Integer(string='Expected Days')
    expected_checkout = fields.Date(compute='_compute_expected_checkout',
                                    string='Expected Checkout')
    add_guests = fields.One2many('hotel.guests', 'booking_id')
    number_person = fields.Integer(string='Number of Persons')
    current_check_out = fields.Boolean(string='Current Checkout')
    nextday_check_out = fields.Boolean(string='Nextday Checkout')
    food_id = fields.One2many('hotel.food', 'booking_id', string="Payments",
                              store=True)
    payment = fields.Integer(string='Total Amount')
    total_food = fields.Integer(string='Total')
    food = fields.Integer(string='Food', related='food_id.sub_total_price')
    order_ref = fields.Char(string='order_ref')
    partner = fields.Char()
    room_name = fields.Integer()

    def _compute_expected_checkout(self):
        for record in self:
            date = record.check_in + relativedelta(days=record.expected_days)
            record.expected_checkout = date

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hotel.booking')
        result = super(HotelBooking, self).create(vals)
        return result

    def action_cancel(self):
        for record in self:
            record.state = "cancel"

    def action_check_in(self):
        for record in self:
            record.state = "check_in"
            if self.number_person == self.env['hotel.guests'].search_count([
                ('booking_id', '=', self.name)]):
                if self.number_person != self.env['ir.attachment'].search_count(
                        [('res_id', '=', self.id)]):
                    raise UserError("address proof is not matched")
            else:
                raise UserError("guest number is not matched")
            for rec in self.room_id:
                rec.write({'state': 'not_available'})
            if record.expected_checkout == fields.Date.today():
                record.current_check_out = True
            if record.expected_checkout == fields.Date.today() + relativedelta(days=1):
                record.nextday_check_out = True


    def action_check_out(self):
        total = []
        p = self.food_id
        for r in p:
            total.append(r.sub_total_price)
        self.total_food = (sum(total))
        for record in self:
            record.state = "check_out"
            for rec in self.room_id:
                rec.write({'state': 'available'})
        view_id = self.env.ref('account.view_move_form').id
        context = {
            'default_move_type': 'out_invoice',
            'default_partner_id': self.partner_id.id,
            'default_journal_id': 17,
            #'default_move_type': 'out_invoice',
            'default_line_ids': [
                {
                    'price_unit': self.payment + self.total_food,
                    'quantity': 1,

                    }
            ]

        }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking Invoice',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'current',
            'context': context
        }



    @api.onchange('expected_days', 'room_id', 'facility_ids')
    def _onchange_payment(self):
        for record in self:
            for rec in self.room_id:
                fac = self.facility_ids
                list = []
                for re in fac:
                    fac_payment = record.expected_days * re.rent
                    list.append(fac_payment)
                    #sum = sum + fac_payment
                y = (sum(list))
                record.payment = record.expected_days * rec.rent + y

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.partner = self.partner_id.name

    @api.onchange('room_id')
    def onchange_room(self):
        self.room_name = self.room_id.name



class HotelInvoice(models.Model):

    _inherit = 'account.move'


    def action_register_payment(self):
        pay = self.env['hotel.booking'].search([('partner_id', '=', self.partner_id.id)])
        for record in pay:
            record.state = 'paid'
        res = super(HotelInvoice, self).action_register_payment()
        return res
