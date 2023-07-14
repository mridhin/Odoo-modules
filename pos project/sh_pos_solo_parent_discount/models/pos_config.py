# -*- coding: utf-8 -*-


from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sc_pwd = fields.Selection(selection_add=[('soloparent', 'Solo Parent')], string='Choose SC/PWD/Solo-Parent')
    check_sc_pwd = fields.Boolean(string='SC/PWD/Solo-Parent')
