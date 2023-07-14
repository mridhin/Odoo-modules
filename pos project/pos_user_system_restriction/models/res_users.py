from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    machine_type = fields.Selection(string="Machine Type", selection=[('laptop','Laptop'),('tablet','Tablet')])
    serial_number = fields.Char(string="Serial Number")
    imei_number = fields.Char(string="IMEI Number")
