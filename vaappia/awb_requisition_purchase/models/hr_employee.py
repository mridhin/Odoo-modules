# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError, ValidationError


class HREmployee(models.Model):
    _inherit = "hr.employee"

    approve_type = fields.Selection([('ceo', 'CEO'),('dm','Department Manager'),
                                    ('om', 'Operations Manager')], string="Approve Type")
    
class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    
    approve_type = fields.Selection([('ceo', 'CEO'),('dm','Department Manager'),
                                    ('om', 'Operations Manager')], string="Approve Type")