# -*- coding: utf-8 -*-
"""imports from odoo lib"""
from odoo import api, fields, models,_
from odoo.exceptions import UserError

"""Inherited model pos.order"""
class PosOrdersInherit(models.Model):
    _inherit = 'pos.order'
    
    #overide the state field
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'), ('invoiced', 'Invoiced'),('voided', 'Voided')],
        'Status', readonly=True, copy=False, default='draft')
    
    def refund(self):
        """Create a copy of order  for refund order, overide this def to change the state"""
        refund_orders = self.env['pos.order']
        for order in self:
            # When a refund is performed, we are creating it in a session having the same config as the original
            # order. It can be the same session, or if it has been closed the new one that has been opened.
            current_session = order.session_id.config_id.current_session_id
            if not current_session:
                raise UserError(_('To return product(s), you need to open a session in the POS %s', order.session_id.config_id.display_name))
            refund_order = order.copy(
                order._prepare_refund_values(current_session)
            )
            for line in order.lines:
                PosOrderLineLot = self.env['pos.pack.operation.lot']
                for pack_lot in line.pack_lot_ids:
                    PosOrderLineLot += pack_lot.copy()
                line.copy(line._prepare_refund_data(refund_order, PosOrderLineLot))
            refund_orders |= refund_order
            """"changing the state to voided"""
            order.state = 'voided'

        return {
            'name': _('Return Products'),
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': refund_orders.ids[0],
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def voidOrder(self):
        """
            This method is called during a POS session, when an order is to be refunded.
            It changes the state of the order to 'voided'.
        """
        self.state = 'voided'

"""Inherited model pos.order.line"""
class PosOrderLineInherit(models.Model):
    _inherit = "pos.order.line"

    def voidOrderline(self):
        """
            This is called during a POS session via rpc when the validate 
            button is pressed and accepts the orderline id of the refunded orderline. 
            From the order_id of the orderline, call voidOrder().
        """
        self.order_id.voidOrder()
        

"""Inherited model pos.order"""
class AccountMoveInherited(models.Model):
    _inherit = 'account.move'
    _decription = 'void the records'
    
    
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
            ('voided', 'Voided'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    

"""Inherited model pos.session"""
class PosSessionInherited(models.Model):
    _inherit = 'pos.session'
    _decription = 'update the jounnal entry record to voided state when the pos order in voided state'
    
    
    def action_pos_session_close(self,balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        """ Inherited to void the payment of the cancelled
        invoice order while session close."""
        # Close CashBox
        res = super(PosSessionInherited, self).action_pos_session_close()
        if self.order_ids:
            order_ids = self.order_ids
            for i in order_ids:
                if (i.state == 'voided') :
                    i.account_move.state = 'voided'
        return res
    