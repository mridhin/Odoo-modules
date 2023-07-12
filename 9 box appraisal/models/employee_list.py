from odoo import models, fields, api


class EmployeeList(models.Model):
    _name = "employee.list"

    name = fields.Many2one('hr.employee', string="Employee Name")
    category = fields.Selection([('hp_lp', 'Potential Gem'),
                                 ('hp_mp', 'High Potential'),
                                 ('hp_hp', 'Star'),
                                 ('mp_lp', 'Inconsistent Player'),
                                 ('mp_mp', 'Core Player'),
                                 ('mp_hp', 'High Performer'),
                                 ('lp_lp', 'Risk'),
                                 ('lp_mp', 'Average Performer'),
                                 ('lp_hp', 'Solid Performer')], compute="compute_category",
                                store=True)
    potential = fields.Selection([('high', 'High'),
                                  ('moderate', 'Moderate'),
                                  ('low', 'Low')],
                                 string="Potential")
    performance = fields.Selection([('high', 'High'),
                                    ('moderate', 'Moderate'),
                                    ('low', 'Low')],
                                   string="Performance")
    appraisal_name = fields.Many2one('appraisal.period',
                                     string="Appraisal Period")
    start_date = fields.Date(string="Appraisal Start Date")
    end_date = fields.Date(string="Appraisal End Date")
    employee_period_id = fields.Many2one('period', string="Employee Period")

    @api.depends('potential', 'performance')
    def compute_category(self):
        if self.potential == 'high' and self.performance == 'low':
            self.category = 'hp_lp'
        if self.potential == 'high' and self.performance == 'moderate':
            self.category = 'hp_mp'
        if self.potential == 'high' and self.performance == 'high':
            self.category = 'hp_hp'
        if self.potential == 'moderate' and self.performance == 'low':
            self.category = 'mp_lp'
        if self.potential == 'moderate' and self.performance == 'moderate':
            self.category = 'mp_mp'
        if self.potential == 'moderate' and self.performance == 'high':
            self.category = 'mp_hp'
        if self.potential == 'low' and self.performance == 'low':
            self.category = 'lp_lp'
        if self.potential == 'low' and self.performance == 'moderate':
            self.category = 'lp_mp'
        if self.potential == 'low' and self.performance == 'high':
            self.category = 'lp_hp'
