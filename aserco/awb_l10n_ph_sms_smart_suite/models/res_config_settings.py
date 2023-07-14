# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class AWBResConfigSettings(models.TransientModel):  
    _inherit = 'res.config.settings'

    sms_gateway_name = fields.Selection(selection=[('smart_gateway','Smart Gateway')])

    # smart_gateway = fields.Boolean(
    #     'Smart SMS Gateway',
    #     default=False,
    #     help="Activating this option will allow the user to use Smart SMS Gateway",
    #     readonly=False
    # )
    smart_gateway_url = fields.Char('Smart API URL', config_parameter='smart_gateway_url')
    smart_gateway_username = fields.Char('Smart API Username', config_parameter='smart_gateway_username')
    smart_gateway_password = fields.Char('Smart API Password', config_parameter='smart_gateway_password')
    # smart_gateway_token = fields.Char('Smart API Token')

    @api.model
    def get_values(self):
      res = super(AWBResConfigSettings, self).get_values()
      params = self.env['ir.config_parameter'].sudo()
      sms_gateway_name = params.get_param('sms_gateway_name', default=False)
      smart_gateway_url = params.get_param('smart_gateway_url', default=False)
      smart_gateway_username = params.get_param('smart_gateway_username', default=False)
      smart_gateway_password = params.get_param('smart_gateway_password', default=False)
      res.update(
          sms_gateway_name=sms_gateway_name,
          smart_gateway_url=smart_gateway_url,
          smart_gateway_username=smart_gateway_username,
          smart_gateway_password=smart_gateway_password,
      )
      return res

    @api.model
    def set_values(self):
        super(AWBResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('sms_gateway_name', self.sms_gateway_name)
        params.set_param('smart_gateway_url', self.smart_gateway_url)
        params.set_param('smart_gateway_username', self.smart_gateway_username)
        params.set_param('smart_gateway_password', self.smart_gateway_password)
