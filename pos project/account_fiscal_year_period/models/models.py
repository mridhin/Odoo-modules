# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear.periods"
    _inherit = ['mail.thread']
    _description = "Fiscal Year"
    _rec_name = 'fiscal_year_id'

    fiscal_year_id = fields.Many2one(
        'account.fiscal.year', required=True, tracking=True)
    code = fields.Char('Code', required=True, tracking=True,
                       default='/', readonly=True)
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company, tracking=True)
    date_start = fields.Date(
        'Start Date', store=True, tracking=True, related='fiscal_year_id.date_from') 
    date_stop = fields.Date('Ending Date', store=True, tracking=True, related='fiscal_year_id.date_to')
    period_ids = fields.One2many(
        'account.month.period', 'fiscalyear_id', 'Periods', tracking=True)
    # For Created quarter records
    period_ids_qua = fields.One2many(
        'account.month.period', 'fiscalyear_id_qua', 'Periods', tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'), ('done', 'Closed')],
        'Status', readonly=True, default='draft', tracking=True)
    comments = fields.Text('Comments')

    @api.onchange('fiscal_year_id')
    def _onchange_fiscal_year_id(self):
        if self.fiscal_year_id:
            self.code = 'FY/'+str(self.fiscal_year_id.name)

    @api.model
    def create(self, vals):
        return super(AccountFiscalyear, self).create(vals)

    def open(self):
        for rec in self:
            rec.write({'state': 'open'})

    def set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def done(self):
        for rec in self:
            rec.period_ids.write({'special': False})
            rec.write({'state': 'done'})

    
    _sql_constraints = [
        ('fiscalyear_per_company_uniq', 'unique(fiscal_year_id,company_id)',
         _('The Fiscal Year must be unique For Periods!'))
    ]

    @api.constrains('date_start', 'date_stop', 'company_id')
    def _check_dates(self):
        for fy in self:
            # Starting date must be prior to the ending date
            date_from = fy.date_start
            date_to = fy.date_stop
            if date_to < date_from:
                raise ValidationError(
                    _('The ending date must not be prior to the starting date.'))

            domain = [
                ('id', '!=', fy.id),
                ('company_id', '=', fy.company_id.id),
                '|', '|',
                '&', ('date_start', '<=', fy.date_start), ('date_stop',
                                                           '>=', fy.date_start),
                '&', ('date_start', '<=', fy.date_stop), ('date_stop',
                                                          '>=', fy.date_stop),
                '&', ('date_start', '<=', fy.date_start), ('date_stop',
                                                           '>=', fy.date_stop),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(
                    _('You can not have an overlap between two fiscal years, please correct the start and/or end dates of your fiscal years.'))

    def create_periods(self):
        period_obj = self.env['account.month.period']
        self.create_periods_quater()
        for rec in self:
            rec.period_ids.unlink()
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_stop)
            index = 1
            while start_date < end_date:
                de = start_date + relativedelta(months=1, days=-1)

                if de > end_date:
                    de = end_date

                period_obj.create({
                    'sequence': index,
                    'code': '%02d/' % int(index) + start_date.strftime('%Y'),
                    'date_start': start_date.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': rec.id,
                    'awb_type': 'monthly'
                })
                start_date = start_date + relativedelta(months=1)
                index += 1

    # # for quater records
    def create_periods_quater(self):
        print("\n\nyess")
        period_obj_qua = self.env['account.month.period']
        for record in self:
            record.period_ids_qua.unlink()
            qua_start_date = fields.Date.from_string(record.date_start)
            qua_end_date = fields.Date.from_string(record.date_stop)
            qua_index = 1
            while qua_start_date < qua_end_date:
                qua_de = qua_start_date + relativedelta(months=3, days=-1)

                if qua_de > qua_end_date:
                    qua_de = qua_end_date

                period_obj_qua.create({
                    'sequence': qua_index,
                    'code': 'Q' + str(qua_index) + '/' + qua_start_date.strftime('%Y'),
                    'date_start': qua_start_date.strftime('%Y-%m-%d'),
                    'date_stop': qua_de.strftime('%Y-%m-%d'),
                    'fiscalyear_id_qua': record.id,
                    'awb_type': 'quarterly',
                })
                qua_start_date = qua_start_date + relativedelta(months=3)
                qua_index += 1


class AccountMonthPeriod(models.Model):
    _name = "account.month.period"
    _description = "Account Month period"
    _inherit = ['mail.thread']
    _rec_name = 'code'
    _order = "date_start asc"

    sequence = fields.Integer('Sequence', default=1)
    awb_type = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly')])
    code = fields.Char('Code', tracking=True)
    special = fields.Boolean('Opening/Closing', tracking=True)
    date_start = fields.Date('From', required=True, tracking=True)
    date_stop = fields.Date('To', required=True, tracking=True)
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear.periods', 'Fiscal Year', tracking=True)
    fiscalyear_id_qua = fields.Many2one(
        'account.fiscalyear.periods', 'Fiscal Year Quarterly', tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='fiscalyear_id.company_id', store=True)

    def get_closest_open_date(self, dates):
        period = self.sudo().with_context(company_id=self.env.company.id).search([('date_start', '<=', dates), (
            'date_stop', '>=', dates), ('special', '=', True), ('company_id', '=', self.env.company.id)], limit=1)
        if period:
            return dates
        else:
            period = self.sudo().with_context(company_id=self.env.company.id).search(
                [('date_start', '>=', dates), ('special', '=', True), ('company_id', '=', self.env.company.id)], limit=1)
            if period:
                return period.date_start
            else:
                return dates

    def get_closest_open_by_period(self, dates):
        period = self.sudo().with_context(company_id=self.env.company.id).search([('date_start', '<=', dates), (
            'date_stop', '>=', dates), ('special', '=', True), ('company_id', '=', self.env.company.id)], limit=1)
        if period:
            return {'date_from': period['date_start'], 'date_to': period['date_stop']}
        else:
            period = self.sudo().with_context(company_id=self.env.company.id).search(
                [('special', '=', True), ('company_id', '=', self.env.company.id)], order='date_start desc', limit=1)
            if period:
                return {'date_from': period['date_start'], 'date_to': period['date_stop']}
            else:
                return False


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_fiscalyear_lock_date(self):
        res = super(AccountMove, self)._check_fiscalyear_lock_date()
        if res:
            for rec in self:
                fiscal_year_obj = self.env['account.fiscalyear.periods']
                period_obj = self.env['account.month.period']
                fiscal_rec = fiscal_year_obj.sudo().with_context(company_id=rec.company_id.id).search(
                    [('date_start', '<=', rec.date), ('date_stop', '>=', rec.date), ('company_id', '=', rec.company_id.id)], limit=1)
                
                if fiscal_rec.state == 'open':
                    period_rec = period_obj.sudo().with_context(company_id=rec.company_id.id).search(
                        [('date_start', '<=', rec.date), ('date_stop', '>=', rec.date), ('fiscalyear_id', '=', fiscal_rec.id)], limit=1)
                    if not period_rec:
                        raise ValidationError(
                            _('The date must be within the period duration.'))
                    elif not period_rec.special:
                        raise ValidationError(
                            _('The Fiscal year period is closed'))
                    else:
                        return True
        else:
            return res
