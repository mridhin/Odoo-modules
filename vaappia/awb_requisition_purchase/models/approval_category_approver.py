# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ApprovalCategoryApprover(models.Model):
    """ Intermediate model between approval.category and res.users
        To know whether an approver for this category is required or not
    """
    _inherit = 'approval.category.approver'

    employee_id = fields.Many2one('hr.employee', related="user_id.employee_id", string='Employee')
    approve_employee_type = fields.Selection(related="employee_id.approve_type", string="Position")
