from odoo import models, fields, api, _
import pandas
from datetime import date, datetime, timedelta


class AppraisalPeriod(models.Model):
    _name = "appraisal.period"
    _description = "Appraisal"

    name = fields.Char(string="Appraisal Period", readonly=True)
    start_date = fields.Date(string="Start Date", readonly=True)
    end_date = fields.Date(string="End Date", readonly=True)
    employee_id = fields.Many2one('hr.employee')
    state = fields.Selection(
        [('inactive', 'Inactive'), ('active', 'Active'), ('close', 'Closed')],
        string='State', compute="compute_state")

    def compute_state(self):
        today = date.today()
        for rec in self:
            if rec.start_date <= today <= rec.end_date:
                rec.state = 'active'
            elif today < rec.start_date:
                rec.state = 'inactive'
            elif today > rec.end_date:
                rec.state = 'close'

    def save_button(self):
        print('sucess')

    def show_graph(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Graph View',
            'view_mode': 'graph',
            'view_type': 'graph',
            'res_model': 'employee.list',
            'target': 'current',
           'domain':[['appraisal_name','=',self.id]],
            'context': {'group_by': ['category']}
        }

    def show_pivot(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pivot View',
            'view_mode': 'pivot',
            'view_type': 'pivot',
            'res_model': 'employee.list',
            'target': 'current',
           'domain':[['appraisal_name','=',self.id]],
            'context': {'group_by': ['category']}
        }


class period(models.Model):
    _name = "period"
    _description = "Appraisal"

    name = fields.Char(string="Name")
    period_id = fields.Many2one('appraisal.period', string="Appraisal Name")
    employee_id = fields.Integer(string="Employee")
    drop = fields.Boolean(string="Droped")
