from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    gitlab_member_id = fields.Char(string="Gitlab Id")
    gitlab_username = fields.Char(string="Gitlab Username")
