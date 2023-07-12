from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    '''Employee Timesheet Reminder'''
    send_employee_reminder = fields.Boolean(
        string="Send Employee Timesheet Reminder?",
    )
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week')
    select_week = fields.Selection([
        ('1', '1 week'),
        ('2', '2 Week'),
        ('3', '3 Week'),
        ('4', '4 Week'),
        ('5', '5 Week'),
        ], 'Select No. of Week')
    time = fields.Float(string='Time')

    ''' Approver TImesheet Feild'''
    send_aprrover_reminder = fields.Boolean(
        string="Send Approver Timesheet Reminder",
    )
    approver_dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week')
    approver_select_week = fields.Selection([
        ('1', '1 week'),
        ('2', '2 Week'),
        ('3', '3 Week'),
        ('4', '4 Week'),
        ('5', '5 Week'),
        ], 'Select No. of Week')
    approver_time = fields.Float(string='Time')

    ''' Send Timesheet reminder to Approver regarding Employee  who have not filled timesheet  '''
    send_aprrover_employee_reminder = fields.Boolean(
        string="Send Approver Timesheet Reminder",
    )
    approver_employee_dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week')
    approver_employee_select_week = fields.Selection([
        ('1', '1 week'),
        ('2', '2 Week'),
        ('3', '3 Week'),
        ('4', '4 Week'),
        ('5', '5 Week'),
        ], 'Select No. of Week')
    approver_employee_time = fields.Float(string='Time')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            send_employee_reminder = self.env['ir.config_parameter'].sudo().get_param('send_employee_reminder'),
            dayofweek = self.env['ir.config_parameter'].sudo().get_param('dayofweek'),
            select_week = self.env['ir.config_parameter'].sudo().get_param('select_week'),
            time = self.env['ir.config_parameter'].sudo().get_param('time'),
            send_aprrover_reminder = self.env['ir.config_parameter'].sudo().get_param('send_aprrover_reminder'),
            approver_dayofweek = self.env['ir.config_parameter'].sudo().get_param('approver_dayofweek'),
            approver_select_week = self.env['ir.config_parameter'].sudo().get_param('approver_select_week'),
            approver_time = self.env['ir.config_parameter'].sudo().get_param('approver_time'),
            send_aprrover_employee_reminder = self.env['ir.config_parameter'].sudo().get_param('send_aprrover_employee_reminder'),
            approver_employee_dayofweek = self.env['ir.config_parameter'].sudo().get_param('approver_employee_dayofweek'),
            approver_employee_select_week = self.env['ir.config_parameter'].sudo().get_param('approver_employee_select_week'),
            approver_employee_time = self.env['ir.config_parameter'].sudo().get_param('approver_employee_time'),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        IrConfig.set_param('send_employee_reminder', self.send_employee_reminder)
        IrConfig.set_param('dayofweek', self.dayofweek)
        IrConfig.set_param('select_week', self.select_week)
        IrConfig.set_param('time', self.time)
        IrConfig.set_param('send_aprrover_reminder', self.send_aprrover_reminder)
        IrConfig.set_param('approver_dayofweek', self.approver_dayofweek)
        IrConfig.set_param('approver_select_week', self.approver_select_week)
        IrConfig.set_param('approver_time', self.approver_time)
        IrConfig.set_param('send_aprrover_employee_reminder', self.send_aprrover_employee_reminder)
        IrConfig.set_param('approver_employee_dayofweek', self.approver_employee_dayofweek)
        IrConfig.set_param('approver_employee_select_week', self.approver_employee_select_week)
        IrConfig.set_param('approver_employee_time', self.approver_employee_time)




