from odoo import fields, models, api
from datetime import datetime
import json
import requests
import base64


class LazadaProductSync(models.TransientModel):
    _name = 'lazada.product.sync'
    _description = 'Lazada Product Sync'

    update_after = fields.Datetime('Update After')
    update_before = fields.Datetime('Update Before')
    item_status = fields.Selection(
        string='Item status',
        selection=[('all', 'All'),
                   ('live', 'Live'),
                   ('inactive', 'Inactive'),
                   ('deleted', 'Deleted'),
                   ('pending', 'Pending'),
                   ('rejected', 'Rejected'),
                   ('sold-out', 'Sold-Out')],
        required=True, default='live')

    def product_sync(self):
        lazada_connector = self.env['lazada.connector'].browse(self._context.get('active_ids', []))
        print(lazada_connector)


        update_after = self.update_after
        update_before = self.update_before
        item_status = self.item_status
        lazada_connector.get_products_from_lazada_all(update_after, update_before, item_status)
        action = self.env["ir.actions.actions"]._for_xml_id("product.product_template_action_all")
        return action
        # return {'type': 'ir.actions.act_window_close'}
