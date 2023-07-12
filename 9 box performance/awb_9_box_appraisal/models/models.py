# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import  UserError


class AppraisalMenu(models.Model):
    _name = "appraisal.menu"
    _description = "Appraisal Menu"
    _rec_name = "name"

    name = fields.Char(string="Appraisal Period", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    period_id = fields.Integer(string="Period Id")

    @api.model
    def create(self, vals):
        appraisal_obj = self.env['appraisal.period'].search([('name', '=', vals['name'])])
        if appraisal_obj:
            raise UserError('Appraisal name already exist')
        values = {
            'name': vals['name'],
            'start_date': vals['start_date'],
            'end_date': vals['end_date'],
        }
        appraisal_period_id = self.env['appraisal.period'].create(values)
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            val = {
                'period_id': appraisal_period_id.id,
                'employee_id': rec.id,
                'name': rec.name
            }
            period_id = self.env['period'].create(val)
        vals['period_id'] = appraisal_period_id.id
        return super(AppraisalMenu, self).create(vals)

    @api.onchange('name', 'start_date', 'end_date')
    def _onchange_appraisal(self):
        appraisal_period_id = self.env['appraisal.period'].search([('id', '=', self.period_id)])
        if self.name:
            appraisal_period_id.write({'name': self.name})
        if self.start_date:
            appraisal_period_id.write({'start_date': self.start_date})
        if self.end_date:
            appraisal_period_id.write({'end_date': self.end_date})

    def unlink(self):
        for rec in self:
            appraisal_period_id = self.env['appraisal.period'].search(
                [('id', '=', rec.period_id)])
            appraisal_period_id.unlink()
        return super(AppraisalMenu, self).unlink()

