from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError


class HotelBooking(models.Model):
    _name = "hotel.booking"
    #_inherit = ['mail.thread']


# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hotel__management(models.Model):
#     _name = 'hotel__management.hotel__management'
#     _description = 'hotel__management.hotel__management'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
