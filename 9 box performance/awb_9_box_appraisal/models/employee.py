from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    potential_field = fields.Selection([('high', 'High'),
                                        ('moderate', 'Moderate'),
                                        ('low', 'Low')],
                                       string="Potential",  readonly=True)

    performance_field = fields.Selection([('high', 'High'),
                                          ('moderate', 'Moderate'),
                                          ('low', 'Low')],
                                         string="Performance",  readonly=True)
    appraisal_value_id = fields.One2many('appraisal.value', 'employee_id',
                                         readonly=True)
    period_id = fields.Many2one('appraisal.period',
                                string='Appraisal Period', readonly=True)
    start_date = fields.Date(string='Appraisal Start Date',  compute="compute_date")
    end_date = fields.Date(string='Appraisal End Date', compute="compute_date")
    category = fields.Selection([('hp_lp', 'Potential Gem'),
                                 ('hp_mp', 'High Potential'),
                                 ('hp_hp', 'Star'),
                                 ('mp_lp', 'Inconsistent Player'),
                                 ('mp_mp', 'Core Player'),
                                 ('mp_hp', 'High Performer'),
                                 ('lp_lp', 'Risk'),
                                 ('lp_mp', 'Average Performer'),
                                 ('lp_hp', 'Solid Performer')],
                                compute="compute_category",
                                store=True)

    @api.depends('potential_field', 'performance_field')
    def compute_category(self):
        for rec in self:
            if rec.potential_field == 'high' and rec.performance_field == 'low':
                rec.category = 'hp_lp'
            if rec.potential_field == 'high' and rec.performance_field == 'moderate':
                rec.category = 'hp_mp'
            if rec.potential_field == 'high' and rec.performance_field == 'high':
                rec.category = 'hp_hp'
            if rec.potential_field == 'moderate' and rec.performance_field == 'low':
                rec.category = 'mp_lp'
            if rec.potential_field == 'moderate' and rec.performance_field == 'moderate':
                rec.category = 'mp_mp'
            if rec.potential_field == 'moderate' and rec.performance_field == 'high':
                rec.category = 'mp_hp'
            if rec.potential_field == 'low' and rec.performance_field == 'low':
                rec.category = 'lp_lp'
            if rec.potential_field == 'low' and rec.performance_field == 'moderate':
                rec.category = 'lp_mp'
            if rec.potential_field == 'low' and rec.performance_field == 'high':
                rec.category = 'lp_hp'

    def compute_date(self):
        for rec in self:
            if rec.period_id:
                rec.start_date = rec.period_id.start_date
                rec.end_date = rec.period_id.end_date
            else:
                self.start_date = False
                self.end_date = False

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        appraisal_period_id = self.env['appraisal.period'].search([])
        for rec in appraisal_period_id:
            val = {
                'period_id': rec.id,
                'employee_id': res.id,
                'name': vals['name']
            }
            period_id = self.env['period'].create(val)
        return res


class AppraisalValues(models.Model):
    _name = "appraisal.value"

    name = fields.Many2one('appraisal.period', string="Appraisal Period")
    category = fields.Selection([('hp_lp', 'Potential Gem'),
                                 ('hp_mp', 'High Potential'),
                                 ('hp_hp', 'Star'),
                                 ('mp_lp', 'Inconsistent Player'),
                                 ('mp_mp', 'Core Player'),
                                 ('mp_hp', 'High Performer'),
                                 ('lp_lp', 'Risk'),
                                 ('lp_mp', 'Average Performer'),
                                 ('lp_hp', 'Solid Performer')],
                                string="Category")
    potential = fields.Selection([('high', 'High'),
                                  ('moderate', 'Moderate'),
                                  ('low', 'Low')],
                                 string="Potential")
    performance = fields.Selection([('high', 'High'),
                                    ('moderate', 'Moderate'),
                                    ('low', 'Low')],
                                   string="Performance")
    employee_id = fields.Many2one('hr.employee')
