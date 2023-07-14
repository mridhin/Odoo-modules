# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _create_account_move(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        for session in self:
            if session.config_id.crm_team_id and session.config_id.crm_team_id.sale_team_prefix_id and \
                    (session.config_id.crm_team_id.sale_team_prefix_id.name == 'TEST' or
                     session.config_id.crm_team_id.awb_pos_provider_is_training_mode):
                print(session.config_id.crm_team_id.awb_pos_provider_is_training_mode)
                data = {'bank_payment_method_diffs': bank_payment_method_diffs or {}}
                data = self._accumulate_amounts(data)
                # data = self._create_non_reconciliable_move_lines(data)
                # data = self._create_bank_payment_moves(data)
                # data = self._create_pay_later_receivable_lines(data)
                # data = self._create_cash_statement_lines_and_cash_move_lines(data)
                # data = self._create_invoice_receivable_lines(data)
                # data = self._create_stock_output_lines(data)
                # if balancing_account and amount_to_balance:
                #     data = self._create_balancing_line(data, balancing_account, amount_to_balance)
                return data
        return super(PosSession, self)._create_account_move(balancing_account=balancing_account,
                                                            amount_to_balance=amount_to_balance,
                                                            bank_payment_method_diffs=bank_payment_method_diffs)

    def _reconcile_account_move_lines(self, data):
        for session in self:
            if session.config_id.crm_team_id and session.config_id.crm_team_id.sale_team_prefix_id and \
                    (session.config_id.crm_team_id.sale_team_prefix_id.name == 'TEST' or
                     session.config_id.crm_team_id.awb_pos_provider_is_training_mode):
                print(session.config_id.crm_team_id)
            return True
        return super(PosSession, self)._reconcile_account_move_lines(data)
