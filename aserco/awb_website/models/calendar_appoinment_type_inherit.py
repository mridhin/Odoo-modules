# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CalendarAppointmentTypeInherit(models.Model):
    _inherit = 'calendar.appointment.type'

    blog_image = fields.Binary(string='Blog Image', attachment=True)
    subtitle = fields.Text(string='Subtitle')
    is_coming_soon = fields.Boolean(string='Is Coming Soon?')

