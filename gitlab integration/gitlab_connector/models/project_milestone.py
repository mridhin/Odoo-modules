from odoo import api, fields, models


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    gitlab_id = fields.Char(string="Gitlab Id", help="gitlab task id")
