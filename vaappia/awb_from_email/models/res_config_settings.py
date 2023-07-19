# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class AWBResConfigSettings(models.TransientModel):  
    _inherit = 'res.config.settings'

    awb_from_email = fields.Char('From Email')


    @api.model
    def get_values(self):
      res = super(AWBResConfigSettings, self).get_values()
      params = self.env['ir.config_parameter'].sudo()
      awb_from_email = params.get_param('awb_from_email', default=False)
      res.update(
          awb_from_email=awb_from_email
      )
      return res

    @api.model
    def set_values(self):
        super(AWBResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('awb_from_email', self.awb_from_email)