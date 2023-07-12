# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    amount_in_words = fields.Char(string='Amount In Text', compute='_get_amount_in_words')

    @api.depends('amount')
    def _get_amount_in_words(self):
        for rec in self:
            amount_text = ''
            if rec.currency_id:
                no_decimal = str(rec.amount).split(".")[0]
                amount_text = rec.currency_id.amount_to_text(int(no_decimal))
                decimal_value = str(rec.amount).split(".")[-1]
                if int(decimal_value) > 0:
                    amount_text = amount_text + ' and ' + decimal_value + '/100 Only'
                else:
                    amount_text = amount_text + ' Only'
            rec.amount_in_words = amount_text.replace(",", "").replace("Peso", "Pesos")






