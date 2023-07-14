# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#  import from odoo lib
from odoo import models, fields 

"""Inherited model res.partner to add field."""
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    ship_to_id = fields.Many2one("res.partner",string="Ship To", readonly=False, domain=[("category_id.name", "=", 'Trucking')])
    delivery_notes = fields.Text('Delivery Notes')
    collection_address = fields.Text('Collection Address')
    collection_notes = fields.Text('Collection Notes')
    agents_id = fields.Many2one('res.partner',string="Agent", readonly=False, domain=[("category_id.name", "=", 'Agent')])
    incentive_eligible = fields.Boolean('Incentive Eligible')
    where_did_you_find_out_about_us = fields.Text('Where did you find out about us?')
    vendor_type = fields.Selection([('inventory','Inventory'), ('non_inventory','Non Inventory')], string="Vendor Type")
    customer_type = fields.Selection([('rt','RT'), ('pv','PV'), ('eu','EU'), ('ws','WS'), ('mt','MT')], string="Customer Type")
    invoice_type = fields.Selection([('dr','DR'), ('si','SI'), ('dr_or_si','DR or SI')], string="Invoice Type")
    collection_area = fields.Char('Collection Area')
    delivery_area_id = fields.Many2one('res.partner.delivery.area', string='Delivery Area')
