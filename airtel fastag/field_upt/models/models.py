from odoo import models, fields, api


class ToleranceProduct(models.Model):
    _inherit = "product.template"

    circle_name = fields.Many2one('rs.circle.name', string="Circle Name")


class CircleProduct(models.Model):
    _inherit = "product.product"

    # circle_name = fields.Many2one('rs.circle.name', string="Circle Name")
   # print('hello')


