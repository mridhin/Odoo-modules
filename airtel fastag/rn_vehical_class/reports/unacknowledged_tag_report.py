from odoo import models, fields, api,_


class unacknowledged_report(models.Model):
    _name = 'unacknowledged.report'
    _description = 'Unacknowledged Report'

    rs_name = fields.Char(string="Transfer Ref")
    rs_barcode = fields.Char(string="Barcode")
    rs_circle_id = fields.Many2one('rs.circle.name', string="Circle Name")
    rs_from_emp_no = fields.Char(string="From EMP ID")
    rs_to_emp_no = fields.Char(string="To EMP ID")
    assigned_id = fields.Many2one('res.users', copy=False, string='Assigned To')

