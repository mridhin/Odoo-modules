from odoo import fields, models, api
from datetime import datetime
import json
import requests
import base64


class LazadaOrderSync(models.TransientModel):
    _name = 'lazada.order.sync'
    _description = 'Lazada Order Sync'

    update_after = fields.Datetime('Update After', required=True)
    update_before = fields.Datetime('Update Before')
    order_status = fields.Selection(
        string='Item status',
        selection=[('all', 'All'),
                   ('unpaid', 'Unpaid'),
                   ('pending', 'Pending'),
                   ('canceled', 'Canceled'),
                   ('ready_to_ship', 'Ready To Ship'),
                   ('delivered', 'Delivered'),
                   ('returned', 'Returned'),
                   ('shipped', 'Shipped'),
                   ('failed', 'Failed'),
                   ('topack', 'To Pack'),
                   ('toship', 'To Ship'),
                   ('shipping', 'Shipping'),
                   ('lost', 'Lost')],
        required=True, default='all')

    def order_sync(self):
        lazada_connector = self.env['lazada.connector'].browse(self._context.get('active_ids', []))
        print(lazada_connector)
        update_after = self.update_after
        update_before = self.update_before
        order_status = self.order_status
        lazada_connector.get_orders_from_lazada_all(update_after, update_before, order_status)
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('is_lazada_order', '=', True)]
        return action
        # return {'type': 'ir.actions.act_window_close'}
