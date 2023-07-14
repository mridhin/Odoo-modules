# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
# inherit the existing model


class TerritoryTerritory(models.Model):
    _name = 'territory.territory'

    name = fields.Char(string="Name")
    region_ids = fields.Many2many('res.country.state', relation='region_service_rel',
                                            column1='region_acc_id',
                                            column2='region_id', string='Regions')


    # technician_ids = fields.Many2many('res.partner', string='Technician')
    technician_ids = fields.Many2many('res.partner', relation='tech_service_rel',
                                            column1='tec_accreditation_id',
                                            column2='tec_id', string='Technician')
    awb_city_id = fields.Many2many('awb.city', relation='city_service_rel',
                                            column1='city_acc_id',
                                            column2='city_id', string='City')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

            
