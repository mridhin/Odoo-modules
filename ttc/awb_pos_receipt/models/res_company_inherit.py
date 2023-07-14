# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompanyPosInherit(models.Model):
    _inherit = 'res.company'
    
    # web_pos = fields.Char(string="Website")
    
    #
    # def get_name(self):
    #     print(self.website)
    #     web = self.website