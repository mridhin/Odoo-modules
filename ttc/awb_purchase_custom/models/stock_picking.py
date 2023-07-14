# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models
import datetime


class Picking(models.Model):
    _inherit = "stock.picking"
    
    def write(self, vals):
        res = super(Picking, self).write(vals)
        if self.picking_type_code in ("incoming", "outgoing"):
            purchase_lines = self.mapped('move_lines').mapped('purchase_line_id')
            if purchase_lines:
                purchase_id = purchase_lines.mapped("order_id")
                if purchase_id:
                    partial = False
                    for line in purchase_id.order_line:
                      if line.qty_received < line.product_qty and (purchase_id.state == 'purchase' or purchase_id.state == 'partial'):
                        partial = True
                        break
                      
                    if partial and purchase_id.state == 'purchase':
                      purchase_id['state'] = 'partial'
                    elif not partial and purchase_id.state == 'partial':
                      purchase_id['state'] = 'purchase'
        return res
    
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    
    def _auto_notify_expiry_alert(self):
        records = self.env['stock.production.lot'].search([('alert_date','!=', False)])
        records.filtered(lambda rec: rec.alert_date.date() == datetime.datetime.today().date())
        for rec in records:
          if rec.alert_date and rec.alert_date.date() == datetime.datetime.today().date():
            pobj_user_id = self.env.user
            message = "The product "+rec.product_id.name+" of lot number "+rec.name+" is Expiring!!! \n Expired Date : "+str(rec.expiration_date and rec.expiration_date.strftime('%m/%d/%Y %H:%M:%S') or "")
            subject =rec.product_id.name+" Expiring Alert!"
            msg_id = pobj_user_id.partner_id.message_post(body=message, subject=subject)
            notif_obj = self.env['mail.notification']
            admin_user_ids = self.env.ref('stock.group_stock_user').sudo().users
            for user_id in admin_user_ids:
                notif_obj.create({'res_partner_id': user_id.partner_id.id, 'is_read': False, 'mail_message_id': msg_id.id, 'notification_type': 'email'})
            mail_id = self.env['mail.mail'].create({'recipient_ids': admin_user_ids.mapped("partner_id").ids, 'mail_message_id': msg_id.id,
                                                    'body_html':message, 'subject': subject})
            mail_id.send(auto_commit=True)
            
class StockOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"
    
    def _auto_notify_minimumstock_alert(self):
        records = self.env['stock.warehouse.orderpoint'].search([])
        for rec in records:
            if rec.product_id and rec.qty_on_hand <= rec.product_min_qty:
                pobj_user_id = self.env.user
                message = rec.product_id.name+ " minimum stock is reached at "+rec.location_id.name+"."
                subject = rec.product_id.name+ " minimum stock alert!"
                msg_id = pobj_user_id.partner_id.message_post(body=message, subject=subject)
                notif_obj = self.env['mail.notification']
                admin_user_ids = self.env.ref('stock.group_stock_user').sudo().users
                for user_id in admin_user_ids:
                    notif_obj.create({'res_partner_id': user_id.partner_id.id, 'is_read': False, 'mail_message_id': msg_id.id, 'notification_type': 'email'})
                mail_id = self.env['mail.mail'].create({'recipient_ids': admin_user_ids.mapped("partner_id").ids, 'mail_message_id': msg_id.id,
                                                        'body_html':message, 'subject': subject})
                mail_id.send(auto_commit=True)
            
            
              
    
    
    
    
    
    
    