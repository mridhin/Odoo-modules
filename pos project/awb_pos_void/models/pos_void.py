# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import fields, models, api,_  # @UnusedImport
from datetime import datetime
from odoo.exceptions import ValidationError,UserError

"""Created to class to define pos void fucntion and also created pos.void.line for relation of pos.void."""
class PosVoid(models.Model):
    _name ='pos.void'
    _description = 'create a new record for void transaction.'
    
    name = fields.Char(default="New", readonly=True)
    date_void = fields.Datetime(string="Date", readonly=True)
    pos_void_line_ids = fields.One2many('pos.void.line', 'pos_void_id', string="OrderLines")
    partner_id = fields.Many2one('res.partner', string="Customer")
    state = fields.Selection([('void', 'Voided')],default='void',string="Status")
    total = fields.Float(string="Total", readonly=True)
    pos_config_id = fields.Many2one('pos.config', string="Terminal")
    pos_session_id = fields.Many2one('pos.session', string="Session")
    pos_user_id = fields.Many2one('res.users', string="Sales Person")
    
    @api.model
    def create_pos_void(self, product_details, other_details):
        """to create a record, while clickng the button from pos."""
        sequence_no = self.env['ir.sequence'].next_by_code('awb_pos_void.void.pos')
        cdate = datetime.now() 
        void_lines = []
        for line in product_details:
            void_lines.append((0, None, self._prepare_void_line(line)))
        if other_details:
            others = other_details[0]
            print(others)
            pos_void = self.env['pos.void'].sudo().create({'partner_id':others['partner_id'] if others.get('partner_id') else False,
                                                           'name':sequence_no,
                                                           'date_void':cdate,
                                                           'pos_config_id': others['config_id'] if others.get('config_id') else False,
                                                           'pos_session_id': others['session_id'] if others.get('session_id') else False, 
                                                           'pos_void_line_ids':void_lines,
                                                           'pos_user_id':others['user_id'] if others.get('user_id') else False})
            
            pos_void.total = sum(pos_void.pos_void_line_ids.mapped('subtotal'))
            return True
    
    def _prepare_void_line(self, line):
        """to prepae lines"""
        return {
            'product_id': line['product_id'],
            'qty': line['qty'],
            'discount': line['discount'],
            'unit_price': line['unit_price'],
            'tax_id': [],
            'product_description':line['product_description']
            
        }
    
class PosVoidLine(models.Model):
    _name = 'pos.void.line'
    _description = 'create void line'
    
    pos_void_id = fields.Many2one('pos.void')
    product_id = fields.Many2one('product.product', string="Product")
    product_description = fields.Char(string="Description")
    qty = fields.Float(string="Quantity")
    tax_id = fields.Many2many('account.tax', string='Taxes')
    discount = fields.Float(string="Discount%")
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute='_compute_total')
    
    @api.depends('unit_price', 'qty', 'discount')
    def _compute_total(self):
        """To calculate total."""
        for i in self:
            pricetotal = 0.00
            price = (i.unit_price) - (i.unit_price * (i.discount/100))
            pricetotal = i.qty * price
            i.subtotal = pricetotal
            

#===============================================================================
# class POSOrders(models.Model):
#     _inherit = 'pos.order'
#     
#     
#     def create(self, vals):
#         print(vals)
#         print(vals)
#         print(vals)
#         ctx = self.env.context
#         res = super(POSOrders, self).create(vals)
#         return res
#     
#     def refund(self):
#         """Create a copy of order  for refund order, overide this def to change the state"""
#         refund_orders = self.env['pos.order']
#         for order in self:
#             # When a refund is performed, we are creating it in a session having the same config as the original
#             # order. It can be the same session, or if it has been closed the new one that has been opened.
#             current_session = order.session_id.config_id.current_session_id
#             if not current_session:
#                 raise UserError(_('To return product(s), you need to open a session in the POS %s', order.session_id.config_id.display_name))
#             refund_order = order.copy(
#                 order._prepare_refund_values(current_session)
#             )
#             for line in order.lines:
#                 PosOrderLineLot = self.env['pos.pack.operation.lot']
#                 for pack_lot in line.pack_lot_ids:
#                     PosOrderLineLot += pack_lot.copy()
#                 line.copy(line._prepare_refund_data(refund_order, PosOrderLineLot))
#             refund_orders |= refund_order
#            
# 
#         return {
#             'name': _('Return Products'),
#             'view_mode': 'form',
#             'res_model': 'pos.order',
#             'res_id': refund_orders.ids[0],
#             'view_id': False,
#             'context': self.env.context,
#             'type': 'ir.actions.act_window',
#             'target': 'current',
#         }
#===============================================================================
    