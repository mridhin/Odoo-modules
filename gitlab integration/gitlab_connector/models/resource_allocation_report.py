# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class ResourceAllocationReport(models.Model):
    _name = "resource.allocation.report"

    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task', string="Task")
    task_stage = fields.Many2many('project.tags', string="Task Stage")
    resource_ids = fields.Many2many('res.users', string="Resource")
    role = fields.Char(string="Role")
    story_points = fields.Char(string="Story Points")

    @api.model
    def resource_allocation_report_action(self):
        self.env['resource.allocation.report'].search([]).unlink()
        task_ids = self.env['project.task'].search([])
        vals = {}
        for task in task_ids:
            role = ''
            if task.user_ids:
                for user in task.user_ids:
                    role = user.partner_id.function
            story_points = 0
            if task.tag_ids:
                for tag in task.tag_ids:
                    if 'Story Point' in tag.name or 'Story Points' in tag.name:
                        story_points = tag.name.split()[0]
            vals = {
                'task_id': task.id,
                'project_id': task.project_id.id,
                'resource_ids': [(6, 0, task.user_ids.ids)],
                'role': role,
                'task_stage': [(6, 0, task.tag_ids.ids)],
                'story_points': story_points
            }
            self.env['resource.allocation.report'].create(vals)
        action = {
            'name': _('Resource Allocation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'resource.allocation.report',
        }
        return action
