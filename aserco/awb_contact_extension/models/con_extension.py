# -*- coding: utf-8 -*-
"""imports from python lib"""
# from mako.pyparser import reserved
import json
"""imports from odoo"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
# inherit the existing model
class Consult(models.Model):
    _inherit = "res.partner.industry"
    _description = "Res_Partner_Industry"
    
   


            
