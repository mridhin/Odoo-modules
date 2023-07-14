# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    field_service_sms_policy_tasks = fields.Selection([('per_order', 'Per Order'),
                                                       ('per_service_template', 'Per Service Template')], default='per_order')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        field_service_sms_policy_tasks = params.get_param('field_service_sms_policy_tasks', default='per_order')
        res.update(
            field_service_sms_policy_tasks=field_service_sms_policy_tasks
        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('field_service_sms_policy_tasks', self.field_service_sms_policy_tasks)
