from odoo import api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    noted_employee_id = fields.Many2one('hr.employee')
