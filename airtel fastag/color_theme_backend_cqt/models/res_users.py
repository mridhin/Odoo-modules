# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    theme_color = fields.Char(name="Theme Color")

    @api.model
    def get_color(self, user):
        employee_id = user.get("id")
        employee_info = self.search(
            [('id', '=', employee_id)])
        message = 'Employee Pin code or password incorrect!'
        if (employee_info):
            return {
                'success': True,
                'employee_id': employee_info.id,
                'employee_theme_color': employee_info.theme_color,
            }
        return {
            'success': False,
            'message': message,
        }
