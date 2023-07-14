from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    awb_cash_difference = fields.Monetary(
        string="Cash Difference", store=False, compute="_compute_awb_cash_difference"
    )
    cash_register_id = fields.Many2one('account.bank.statement', compute='_compute_cash_all', string='Cash Register', store=True)
    statement_ids = fields.One2many('account.bank.statement', 'pos_session_id', string='Cash Statements', readonly=True)

    @api.depends("cash_register_id")
    def _compute_awb_cash_difference(self):
        for record in self:
            record.awb_cash_difference = 0
            if record.cash_register_id:
                account_bank_statement_line = record.cash_register_id.line_ids.filtered(
                    lambda r: "Cash difference observed during the counting"
                    in r.payment_ref
                )
                record.awb_cash_difference = sum(
                    account_bank_statement_line.mapped("amount")
                )

    @api.depends('config_id', 'statement_ids', 'payment_method_ids')
    def _compute_cash_all(self):
        # Only one cash register is supported by point_of_sale.
        for session in self:
            session.cash_journal_id = session.cash_register_id = session.cash_control = False
            cash_payment_methods = session.payment_method_ids.filtered('is_cash_count')
            if not cash_payment_methods:
                continue
            for statement in session.statement_ids:
                if statement.journal_id == cash_payment_methods[0].journal_id:
                    session.cash_control = session.config_id.cash_control
                    session.cash_journal_id = statement.journal_id.id
                    session.cash_register_id = statement.id
                    break  # stop iteration after finding the cash journal



class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    pos_session_id = fields.Many2one('pos.session', string="Session", copy=False)

    @api.depends("awb_cash_difference")
    def _compute_awb_cash_difference(self):
        for record in self:
            record.awb_cash_difference = 0
            account_bank_statement_line = record.statement_line_ids.filtered(
                    lambda r: "Cash difference observed during the counting"
                    in r.payment_ref
                )
            record.awb_cash_difference = sum(
                    account_bank_statement_line.mapped("amount")
                )
