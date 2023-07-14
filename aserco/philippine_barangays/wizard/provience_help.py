from odoo import api, fields, models


class ProvinceHelp(models.TransientModel):
    _name = 'provience.help'
    _description = 'help'

    name = fields.Html("Instruction")
