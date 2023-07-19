# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import pytz


class AccountAnalyticLine(models.Model):
    _inherit = "hr.employee"
    
    ''' Send Mail To Employee'''
    @api.model
    def send_employee_timesheet_reminder_notification(self):
        today = fields.Date.context_today(self)
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        day = IrConfigParameter.get_param("dayofweek")
        send_reminder = IrConfigParameter.get_param("send_employee_reminder")
        select_week = IrConfigParameter.get_param("select_week")
        time = IrConfigParameter.get_param("time")

        timezone = self.env.user.tz or pytz.utc
        local_zone = pytz.timezone(timezone)
        now = datetime.now(local_zone)
        current_time = now.strftime("%H:%M")

        date_start_1week = now + relativedelta(weeks=-2, weekday=5)
        date_end_1week = now + relativedelta(weeks=-1, weekday=4)
        
        date_start_2week = now + relativedelta(weeks=-3, weekday=5)
        date_end_2week = now + relativedelta(weeks=-1, weekday=4)

        date_start_3week = now + relativedelta(weeks=-4, weekday=5)
        date_end_3week = now + relativedelta(weeks=-1, weekday=4)

        date_start_4week = now + relativedelta(weeks=-5, weekday=5)
        date_end_4week = now + relativedelta(weeks=-1, weekday=4)
        
        date_start_5week = now + relativedelta(weeks=-6, weekday=5)
        date_end_5week = now + relativedelta(weeks=-1, weekday=4)
        
        minutes = float(time)*60
        hours, minutes = divmod(minutes, 60)
        time = ("%02d:%02d"%(hours,minutes))

        if send_reminder and  now.weekday() == int(day) and current_time == time:
            employee_ids = self.env['hr.employee'].search([]) 
            for rec in employee_ids:
                if select_week == '1':
                    timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', rec.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_1week.date()), ('date', '<=',  date_end_1week.date())])
                    print('Timesheet\n\n',timesheet_ids)
                    timesheet_ids1 = self.env['account.analytic.line'].search([('employee_id', '=', rec.id)])

                elif select_week == '2':
                    timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', rec.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_2week.date()), ('date', '<=',  date_end_2week.date())])
                    timesheet_ids1 = self.env['account.analytic.line'].search([('employee_id', '=', rec.id)])
         
                elif select_week == '3':
                    timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', rec.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_3week.date()), ('date', '<=',  date_end_3week.date())])
                    timesheet_ids1 = self.env['account.analytic.line'].search([('employee_id', '=', rec.id)])

                elif select_week == '4':
                    timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', rec.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_4week.date()), ('date', '<=',  date_end_4week.date())])
                    timesheet_ids1 = self.env['account.analytic.line'].search([('employee_id', '=', rec.id)])

                elif select_week == '5':
                    timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', rec.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_5week.date()), ('date', '<=',  date_end_5week.date())])
                    timesheet_ids1 = self.env['account.analytic.line'].search([('employee_id', '=', rec.id)])
                template_id =  self.env['ir.model.data']._xmlid_to_res_id('awb_timesheet_notification.email_timesheet_reminder_template')
                template_browse = self.env['mail.template'].browse(template_id)
                if template_browse and timesheet_ids:
                    values = template_browse.generate_email(timesheet_ids[0].employee_id.id, ['subject', 'body_html', 'email_from', 'email_to'])
                    values['subject'] = "Employee Timesheet Reminder"
                    # values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email
                    msg_id = self.env['mail.mail'].create({
                        'body_html': values['body_html'],
                        'subject':values['subject'],
                        'email_to':timesheet_ids[0].employee_id.work_email,})
                    if msg_id:
                        msg_id.send()

    ''' Send Email To Approver Regarding Submitted Timesheet '''
    @api.model
    def send_approver_timesheet_reminder_notification(self):
        today = fields.Date.context_today(self)
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        day = IrConfigParameter.get_param("approver_dayofweek")
        send_reminder = IrConfigParameter.get_param("send_aprrover_reminder")
        select_week = IrConfigParameter.get_param("approver_select_week")
        time = IrConfigParameter.get_param("approver_time")

        timezone = self.env.user.tz or pytz.utc
        local_zone = pytz.timezone(timezone)
        now = datetime.now(local_zone)
        current_time = now.strftime("%H:%M")

        date_start_1week = now + relativedelta(weeks=-2, weekday=5)
        date_end_1week = now + relativedelta(weeks=-1, weekday=4)
        
        date_start_2week = now + relativedelta(weeks=-3, weekday=5)
        date_end_2week = now + relativedelta(weeks=-1, weekday=4)

        date_start_3week = now + relativedelta(weeks=-4, weekday=5)
        date_end_3week = now + relativedelta(weeks=-1, weekday=4)

        date_start_4week = now + relativedelta(weeks=-5, weekday=5)
        date_end_4week = now + relativedelta(weeks=-1, weekday=4)
        
        date_start_5week = now + relativedelta(weeks=-6, weekday=5)
        date_end_5week = now + relativedelta(weeks=-1, weekday=4)
        
        minutes = float(time)*60
        hours, minutes = divmod(minutes, 60)
        time = ("%02d:%02d"%(hours,minutes))
        if send_reminder and  now.weekday() == int(day) and current_time == time:
            project_ids = self.env['project.task'].search([])
            if project_ids:
                for pro in project_ids:
                    if select_week == '1':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'submit'), ('date', '>=', date_start_1week.date()), ('date', '<=',  date_end_1week.date())])
                        # print('\n\nname\n\n', '\n\nProject name\n\n',pro.name, '\n\nppp\n\n', pro.project_id.user_id.name, '\n\ntttt', timesheet_ids)

                    elif select_week == '2':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'submit'), ('date', '>=', date_start_2week.date()), ('date', '<=',  date_end_2week.date())])

                    elif select_week == '3':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'submit'), ('date', '>=', date_start_3week.date()), ('date', '<=',  date_end_3week.date())])

                    elif select_week == '4':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'submit'), ('date', '>=', date_start_4week.date()), ('date', '<=',  date_end_4week.date())])

                    elif select_week == '5':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'submit'), ('date', '>=', date_start_5week.date()), ('date', '<=',  date_end_5week.date())])
                       
                    # if any(timesheet.validated_status == "submit" for timesheet in timesheet_ids):
                    template_id =  self.env['ir.model.data']._xmlid_to_res_id('awb_timesheet_notification.email_approver_timesheet_reminder_template')
                    template_browse = self.env['mail.template'].browse(template_id)
                    if template_browse and timesheet_ids:
                        values = template_browse.generate_email(timesheet_ids[0].project_id.user_id.id, ['subject', 'body_html', 'email_from', 'email_to'])
                        values['subject'] = "Approver Timesheet Reminder"
                        # values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email
                        msg_id = self.env['mail.mail'].create({
                            'body_html': values['body_html'],
                            'subject':values['subject'],
                            'email_to':timesheet_ids[0].project_id.user_id.login,})
                        if msg_id:
                            msg_id.send()

    ''' Send Email To Approver Regarding Timesheet Not Submitted '''
    @api.model
    def send_approver_employee_timesheet_reminder_notification(self):
        today = fields.Date.context_today(self)
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        day = IrConfigParameter.get_param("approver_employee_dayofweek")
        send_reminder = IrConfigParameter.get_param("send_aprrover_employee_reminder")
        select_week = IrConfigParameter.get_param("approver_employee_select_week")
        time = IrConfigParameter.get_param("approver_employee_time")

        timezone = self.env.user.tz or pytz.utc
        local_zone = pytz.timezone(timezone)
        now = datetime.now(local_zone)
        current_time = now.strftime("%H:%M")

        date_start_1week = now + relativedelta(weeks=-2, weekday=5)
        date_end_1week = now + relativedelta(weeks=-1, weekday=4)
        
        date_start_2week = now + relativedelta(weeks=-3, weekday=5)
        date_end_2week = now + relativedelta(weeks=-1, weekday=4)

        date_start_3week = now + relativedelta(weeks=-4, weekday=5)
        date_end_3week = now + relativedelta(weeks=-1, weekday=4)

        date_start_4week = now + relativedelta(weeks=-5, weekday=5)
        date_end_4week = now + relativedelta(weeks=-1, weekday=4)
        
        date_start_5week = now + relativedelta(weeks=-6, weekday=5)
        date_end_5week = now + relativedelta(weeks=-1, weekday=4)
        
        minutes = float(time)*60
        hours, minutes = divmod(minutes, 60)
        time = ("%02d:%02d"%(hours,minutes))
        if send_reminder and  now.weekday() == int(day) and current_time == time:
            project_ids = self.env['project.task'].search([])
            if project_ids:
                for pro in project_ids:
                    if select_week == '1':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_1week.date()), ('date', '<=',  date_end_1week.date())])
                        # print('\n\nname\n\n', '\n\nProject name\n\n',pro.name, '\n\nppp\n\n', pro.project_id.user_id.name, '\n\ntttt', timesheet_ids)

                    elif select_week == '2':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_2week.date()), ('date', '<=',  date_end_2week.date())])

                    elif select_week == '3':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_3week.date()), ('date', '<=',  date_end_3week.date())])

                    elif select_week == '4':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_4week.date()), ('date', '<=',  date_end_4week.date())])

                    elif select_week == '5':
                        timesheet_ids = self.env['account.analytic.line'].search([('task_id', '=', pro.id), ('validated_status', '=', 'draft'), ('date', '>=', date_start_5week.date()), ('date', '<=',  date_end_5week.date())])
                    template_id =  self.env['ir.model.data']._xmlid_to_res_id('awb_timesheet_notification.email_approver_employee_timesheet_reminder_template')
                    template_browse = self.env['mail.template'].browse(template_id)
                    if template_browse and timesheet_ids:
                        values = template_browse.generate_email(timesheet_ids[0].project_id.user_id.id, ['subject', 'body_html', 'email_from', 'email_to'])
                        values['subject'] = "Approver Employee Timesheet Reminder"
                        # values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email
                        msg_id = self.env['mail.mail'].create({
                            'body_html': values['body_html'],
                            'subject':values['subject'],
                            'email_to':timesheet_ids[0].project_id.user_id.login,})
                        if msg_id:
                            msg_id.send()



# class AccountAnalyticLine(models.Model):
#     _inherit = "account.analytic.line"

    
#     @api.model_create_multi
#     def create(self, vals_list):
#         # OVERRIDE


#         res = super(AccountAnalyticLine, self).create(vals_list)
#         self.env['timesheet.weekly.details'].create({'analytic_account_line_id': res.id, 'is_timesheet': True, 'name': res.employee_id.name})

#         return res


class TimesheetWeeklyDetails(models.Model):
    _name = "timesheet.weekly.details"
    _description = "Timesheet Weekly Details"

    name = fields.Char(required=True)
    is_timesheet = fields.Boolean()
    analytic_account_line_id = fields.Many2one('account.analytic.line')
    timesheet_line_ids = fields.One2many('timesheet.weekly.details.line', 'timesheet_weekly_id',  string="Timesheet Weekly Line")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Datetime()


    # @api.model
    # def send_timesheet_reminder_notification(self):
  
    #     if send_reminder and  date.today().weekday() == int(day):
    #         for partner in self.env['account.analytic.line'].search([('validated_status', '=', 'draft')], limit=1):
    #             template_id = self.env.ref('awb_timesheet_notification.email_timesheet_reminder_template')
    #             print('Partner\n\n', partner.date, '\n\nfff', 'ggggggggg\n\n', template_id)
    #             template_id.send_mail(partner.employee_id.id, force_send=True)


class TimesheetWeeklyDetails(models.Model):
    _name = "timesheet.weekly.details.line"
    _description = "Timesheet Weekly Details Line"

    name = fields.Char(required=True)
    is_timesheet = fields.Boolean()
    analytic_account_line_id = fields.Many2one('account.analytic.line')
    date = fields.Datetime()
    timesheet_weekly_id = fields.Many2one('timesheet.weekly.details')