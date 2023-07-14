# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProjectServiceTemplate(models.Model):
    _description = 'Service Template'
    _name = "project.service.template"
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    project_id = fields.Many2one("project.project", string="Project", required=True)
    service_product = fields.Many2one('product.template', string="Service Product", required=True)
    active = fields.Boolean(string="Active", default=True)
    template_details_lines = fields.One2many("project.service.template.line", "template_id", string="Template Details")

    def name_get(self):
        result = []
        for service in self:
            name = str(service.project_id.name) + ' - ' + str(service.service_product.name)
            result.append((service.id, name))
        return result

    @api.onchange("project_id", "service_product")
    def _onchange_name(self):
        for record in self:
            if record.project_id and record.service_product:
                record.name = str(record.project_id.name) + ' - ' + str(record.service_product.name)

    @api.constrains("project_id", "service_product")
    def _check_record(self):
        for record in self:
            if record.project_id and record.service_product:
                service_template_rec = self.env['project.service.template'].search([('project_id', '=', int(record.project_id.id)),
                                                                                    ('service_product', '=', int(record.service_product.id))])
                if len(service_template_rec) > 1:
                    raise ValidationError(str(record.project_id.name) + ' ' + str(record.service_product.name) + ' ' + 'Service Template combination already exists.')


class TemplateDetails(models.Model):
    _name = 'project.service.template.line'

    template_id = fields.Many2one("project.service.template", string="Template Id")
    stage_id = fields.Many2one("project.task.type", string="Stage", required=True)
    sms_template_id = fields.Many2one("sms.template", string="Template", required=True)
    remark = fields.Char(string="Remark")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sms_template = fields.Many2one("project.service.template", string="SMS Template")
