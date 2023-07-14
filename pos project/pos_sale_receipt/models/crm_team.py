# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    starting_sequence_number = fields.Integer(string='Starting Sequence number')
    current_sequence_number = fields.Integer(string='Current Sequence number',
                                             store=True)
    # compute='onchange_starting_sequence_number',
    ending_sequence_number = fields.Integer(string='Ending Sequence number', store=True)
    threshold_sequence_number = fields.Integer(string='Threshold Sequence number')
    sale_team_prefix_id = fields.Many2one(string="Sale Team Prefix", comodel_name='sale.team.prefix', copy=False, required=True)

    @api.depends('ending_sequence_number')
    def onchange_ending_sequence_number(self):
        for record in self:
            if record.ending_sequence_number < record.current_sequence_number:
                raise UserError(_('Ending sequence number should be greater than current sequence number.'))

    @api.onchange('awb_pos_provider_is_training_mode')
    def onchange_awb_pos_provider_is_training_mode(self):
        if self.awb_pos_provider_is_training_mode:
            # Set sale_team_prefix_id as TEST.
            self.sale_team_prefix_id = self.env['sale.team.prefix'].search([('name', '=', 'TEST')], limit=1)
            self.ensure_one() # Ensure there is only one record.
            # Return values where name = TEST. This will prevent the user from choosing
            #   any value besides TEST.
            return {'domain': {'sale_team_prefix_id': [('name','=', 'TEST')]}}
        else:
            # Set sale_team_prefix_id as OR by default.
            # This is to prevent the value TEST from being chosen if the user
            #   enabled training mode then turned it off.
            self.sale_team_prefix_id = self.env['sale.team.prefix'].search([('name', '=', 'OR')])
            self.ensure_one() # Ensure there is only one record.
            # Return values where name != TEST. This will hide the value TEST if
            #   training mode is off.
            return {'domain': {'sale_team_prefix_id': [('name','not ilike', '%test%')]}}
    
    @api.constrains('awb_pos_provider_is_training_mode', 'sale_team_prefix_id')
    def _validate_prefix(self):
        for record in self:
            if not record.awb_pos_provider_is_training_mode:
                if not record.sale_team_prefix_id in self.env['sale.team.prefix'].search([('name', 'not ilike', '%test%')]):
                    raise ValidationError(_("Sale team prefix must not include 'TEST' when not in training mode."))

