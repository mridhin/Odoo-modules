# -*- coding: utf-8 -*-
"""imports from python lib"""
# from mako.pyparser import reserved
import json
"""imports from odoo"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
# create a new model
class Consult(models.Model):
    _name = "service.offered"
    _description = "service_offered"
    
    # created a new fields for new model
    name =  fields.Char(string='Name')
    ser_type = fields.Selection([
        ('products', 'Products'),
        ('services', 'Services'),
    ], string='Type', required=True, tracking=True)
    tag = fields.Char(string='Tags', compute='_compute_tag')
    # For Archived the offer type record
    active = fields.Boolean(string="Active",default=True)
    # compute field for ser_type
    @api.depends('name')
    def _compute_tag(self):
        for record in self:
            record.tag = ' '
            if record:
                if record.ser_type:
                    record.tag = record.ser_type + '/' + record.name
                    
    


            
