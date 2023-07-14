# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

import re
import pytz

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    increase_sequence = fields.Boolean(string='Increase Sequence', default=False)
    send_warning = fields.Boolean(string='Show Warning')
    remaining_sequence_number = fields.Integer(string='Remaning sequence', readonly=True, default=0)
    next_sequence_number = fields.Char(string='Next Sequence Number', default='')

    @api.model
    def create_from_ui(self, orders, draft=False):
        # self.env['pos.order'].sudo().search([('pos_reference', 'ilike', orders[l]['data']['uid'])])
        for l in range(0, len(orders)):
            pos_order_id = self.env['pos.order'].sudo().search([('pos_reference', 'ilike', orders[l]['data']['uid'])],limit=1)
            order_refund_id = pos_order_id.id if pos_order_id else False
            _logger.info('***** order_refund_id *****')
            for li in orders[l]['data']['lines']:
                li[2]['refunded_orderline_id'] = order_refund_id
        res = super(PosOrder, self).create_from_ui(orders, draft)
        order_ids = [d['id'] for d in res if 'id' in d]
        return self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)],
                                                 fields=['id', 'pos_reference', 'send_warning',
                                                         'remaining_sequence_number'])

    def _export_for_ui(self, order):
        """
            This method is originally from pos_order. Inheriting the method via super 
            does not work since the base method is throwing an error because of this
                re.search('([0-9]|-){14}', order.pos_reference).group(0),
            which is searching for the sequence number with 14 digits in pos_reference 
            and the custom sequence is not 14 digits (minimum of 6 and can be adjusted).

            This is why the code below is copy and pasted from the original method,
            with the uid altered with the new RegEx search condition.
                re.search('([0-9]|-){6,}', order.pos_reference).group(0),
            Meaning capture (any of (digit, literally "-")), at least 6 times.

            If there is a better way of inheriting this, please update the code below.
        """
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        self = self.filtered(lambda x: x.state != 'voided')
        return {
            'lines': [[0, 0, line] for line in order.lines.export_for_ui()],
            'statement_ids': [[0, 0, payment] for payment in order.payment_ids.export_for_ui()],
            'name': order.pos_reference,
            'uid': re.search('([0-9]|-){6,}', order.pos_reference).group(0),
            'amount_paid': order.amount_paid,
            'amount_total': order.amount_total,
            'amount_tax': order.amount_tax,
            'amount_return': order.amount_return,
            'pos_session_id': order.session_id.id,
            'is_session_closed': order.session_id.state == 'closed',
            'pricelist_id': order.pricelist_id.id,
            'partner_id': order.partner_id.id,
            'user_id': order.user_id.id,
            'sequence_number': order.sequence_number,
            'creation_date': order.date_order.astimezone(timezone),
            'fiscal_position_id': order.fiscal_position_id.id,
            'to_invoice': order.to_invoice,
            'to_ship': order.to_ship,
            'state': order.state,
            'account_move': order.account_move.id,
            'id': order.id,
            'is_tipped': order.is_tipped,
            'tip_amount': order.tip_amount,
        }

    @api.model
    def _complete_values_from_session(self, session, values):
        res = super(PosOrder, self)._complete_values_from_session(session, values)
        crm_team_record = session.config_id.crm_team_id
        res['increase_sequence'] = True
        if crm_team_record.threshold_sequence_number < crm_team_record.current_sequence_number:
            res['send_warning'] = True
            res[
                'remaining_sequence_number'] = crm_team_record.ending_sequence_number - crm_team_record.current_sequence_number
        if not crm_team_record.awb_pos_provider_is_training_mode and \
                (crm_team_record.ending_sequence_number <= crm_team_record.current_sequence_number):
            raise ValidationError(_('Receipt number reached threshold sequence number.'))
        if crm_team_record:
            next_sequence_number_sufix = 0
            current_sequence_number_with_format = 0
            next_sequence_number_complete = 0
            return_order = self.env.context.get('return_pos_order_restrict')
            if return_order:
                res['increase_sequence'] = False
                res['pos_reference'] = ''
                res['next_sequence_number'] = ''
            else:
                if crm_team_record.sale_team_prefix_id and crm_team_record.ending_sequence_number > crm_team_record.current_sequence_number and \
                        res['increase_sequence']:
                    res['increase_sequence'] = False
                    # Check the value of awb_pos_provider_is_training_mode
                    if crm_team_record.awb_pos_provider_is_training_mode:
                        crm_team_record.current_sequence_number = 0
                    else:
                        crm_team_record.current_sequence_number += 1
                    next_sequence_number_sufix = crm_team_record.current_sequence_number + 1
                    current_sequence_number_with_format = str(crm_team_record.current_sequence_number).zfill(6)
                    next_sequence_number_complete = str(next_sequence_number_sufix).zfill(6)
                if crm_team_record.ending_sequence_number > pow(9, 6):
                    length_of_ending_sequence_number = len(str(crm_team_record.ending_sequence_number))
                    current_sequence_number_with_format = str(crm_team_record.current_sequence_number).zfill(
                        length_of_ending_sequence_number)
                    next_sequence_number_complete = str(next_sequence_number_sufix).zfill(
                        length_of_ending_sequence_number)
                res['pos_reference'] = crm_team_record.sale_team_prefix_id.name + ' ' + str(
                    current_sequence_number_with_format)
                res['next_sequence_number'] = crm_team_record.sale_team_prefix_id.name + ' ' + str(
                    next_sequence_number_complete)
        return res

    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        res['pos_order_id'] = self.id
        return res
