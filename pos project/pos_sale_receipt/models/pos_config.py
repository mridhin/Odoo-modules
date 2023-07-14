from odoo import models, fields, api
from odoo import models, fields, api, exceptions, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sale_team_present = fields.Boolean(string='Sale Team Present', compute='_compute_sale_team_present')
    module_account = fields.Boolean(default=False, string='Invoicing', readonly=False,
                                    states={'draft': [('readonly', False)]})

    @api.constrains('module_account', 'sale_team_present', 'awb_pos_provider_is_training_mode')
    def _check_module_account(self):
        for record in self:
            if record.sale_team_present and not record.module_account:
                continue
            if record.sale_team_present and record.crm_team_id.awb_pos_provider_is_training_mode:
                if record.module_account:
                    raise exceptions.ValidationError(
                        _("Invoicing should not be checked when Tranning mode is True."))

    @api.onchange('module_account', 'crm_team_id')
    def _onchange_module_account(self):
        if self.crm_team_id and self.crm_team_id.awb_pos_provider_is_training_mode:
            self.module_account = False

    # @api.depends('crm_team_id', 'crm_team_id.sale_team_prefix_id', 'crm_team_id.awb_pos_provider_is_training_mode')
    def _compute_sale_team_present(self):
        for config in self:
            if config.crm_team_id.sale_team_prefix_id.name == 'TEST' or \
                    config.crm_team_id.awb_pos_provider_is_training_mode:
                config.sale_team_present = True
            else:
                config.sale_team_present = False


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    awb_pos_provider_is_training_mode = fields.Boolean(
        help="If you are using this Training mode your journal entries and cash flow will not calculated",
        readonly='awb_pos_provider_is_training_mode_readonly')
    sale_team_prefix_id = fields.Many2one('sale.team.prefix')

    # @api.depends('crm_team_id', 'crm_team_id.sale_team_prefix_id')
    # def _compute_sale_team_present(self):
    #     for config in self:
    #         if config.crm_team_id.sale_team_prefix_id.name == 'TEST' or config.awb_pos_provider_is_training_mode:
    #             config.sale_team_present = True
    #         else:
    #             config.sale_team_present = False
    #         if config.sale_team_present:
    #             config.module_account.read

    @api.constrains('awb_pos_provider_is_training_mode', 'sale_team_prefix_id')
    def _check_sale_team_prefix(self):
        for team in self:
            if team.awb_pos_provider_is_training_mode and team.sale_team_prefix_id.name != 'TEST':
                raise exceptions.ValidationError(_("Sale team prefix must be 'TEST' when in training mode."))
            if not team.awb_pos_provider_is_training_mode and not team.sale_team_prefix_id:
                raise exceptions.ValidationError(_("Sale team prefix is required."))
