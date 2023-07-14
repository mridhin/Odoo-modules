from odoo import fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    gitlab_id = fields.Char(string="Gitlab Id", help="gitlab project id")
    is_gitlab = fields.Boolean(string="Is Gitlab", default=False)


class Task(models.Model):
    _inherit = "project.task"

    gitlab_issue_id = fields.Char(string="Gitlab Task Id", help="gitlab task id")
    due_date = fields.Char(string="Due Date")
    milestone_id = fields.Many2one("project.milestone",string="Milestone",domain=[('project_id','=','project_id')])
    estimate_time = fields.Char(string="Estimate Time")


class ProjectTags(models.Model):
    _inherit = "project.tags"

    gitlab_label_id = fields.Char(string="Gitlab Label Id", help="gitlab label id")


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    gitlab_id = fields.Char(string="Gitlab Label Id", help="gitlab label id")
