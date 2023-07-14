# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import logging, time

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('x_studio_preferred_date')
    def _onchange_service_date(self):
        if self.x_studio_preferred_date and self.x_studio_preferred_date < fields.Date.today():
            self.x_studio_preferred_date = False

    def action_confirm(self):
        rec = super(SaleOrder, self).action_confirm()
        config_params = self.env['ir.config_parameter'].sudo()
        field_service_sms_policy_sales = config_params.get_param('field_service_sms_policy_sales')
        if field_service_sms_policy_sales == 'per_service_template':
            for rec in self:
                if (rec.state == 'sale'):
                    line_temp_id = {line.product_id.sms_template.id for line in rec.order_line}
                    _logger.info(f'SMS:: SMS template {line_temp_id}')
                    if line_temp_id:
                        for msg in line_temp_id:
                            message_body = 'Happy Day!' \
                                           '\nYour service request is confirmed.' \
                                           '\nYour appointment date is on %s' \
                                           '\nKindly prepare all necessary permits for fast and easy service.' \
                                           '\nThank you and Stay Safe!' \
                                           % (rec.x_studio_preferred_service_schedule.x_name if rec.x_studio_preferred_service_schedule else rec.x_studio_preferred_date)
                            sms_template = self.env['sms.template'].search([('name', 'like', 'Sale Order: Booking Confirmation')], limit=1)
                            if sms_template:
                                date = rec.x_studio_preferred_service_schedule.x_name if rec.x_studio_preferred_service_schedule else rec.x_studio_preferred_date
                                message_body = sms_template.body.replace('x_studio_preferred_service_schedule', str(date)).replace('partner_name', rec.partner_id.name)
                            try:
                                self.env['sms.api'].sudo()._send_sms(rec.x_studio_contact_no_1, message_body)
                                _logger.info(f'SMS:: SMS sent successfully for {rec.name}')
                            except Exception as e:
                                _logger.error(f'SMS:: Error has encountered in sending SMS: {e}')
                                # if str(e) == "Sorry. Can't send SMS because of insufficient credits":
                                #     raise ValidationError("Sorry. Can't send SMS because of insufficient credits")
                            time.sleep(10)
        elif field_service_sms_policy_sales == 'per_order':
            for rec in self:
                if (rec.state == 'sale'):
                    message_body = 'Happy Day!' \
                                   '\nYour service request is confirmed.' \
                                   '\nYour appointment date is on %s' \
                                   '\nKindly prepare all necessary permits for fast and easy service.' \
                                   '\nThank you and Stay Safe!' \
                                   % (
                                       rec.x_studio_preferred_service_schedule.x_name if rec.x_studio_preferred_service_schedule else rec.x_studio_preferred_date)
                    sms_template = self.env['sms.template'].search(
                        [('name', 'like', 'Sale Order: Booking Confirmation')], limit=1)
                    if sms_template:
                        date = rec.x_studio_preferred_service_schedule.x_name if rec.x_studio_preferred_service_schedule else rec.x_studio_preferred_date
                        message_body = sms_template.body.replace('x_studio_preferred_service_schedule',
                                                                 str(date)).replace('partner_name', rec.partner_id.name)
                    try:
                        self.env['sms.api'].sudo()._send_sms(rec.x_studio_contact_no_1, message_body)
                        _logger.info(f'SMS:: SMS sent successfully for {rec.name}')
                    except Exception as e:
                        _logger.error(f'SMS:: Error has encountered in sending SMS: {e}')
        return rec
