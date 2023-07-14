# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
import re
import ast

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _get_custom_access_token(self):
        rating_rec = self.env["rating.rating"].sudo().search([('partner_id', '=', self.partner_id.id), ('res_id', '=', self.id)], order='id desc', limit=1)
        if rating_rec:
            self.custom_access_token = rating_rec.access_token

    custom_access_token = fields.Char('Security Token', help="Access token to set the rating of the value", store = True)
    state = fields.Char(compute="_compute_stage_id", store=True)
    sending_date = fields.Date('Completed Sending Date')
    state_lines = fields.Text("State lines")
    custom_stage_id = fields.Many2one('project.task.type', string='Stage',
        related="stage_id")
    custom_is_closed = fields.Boolean(string='Custom Closed',compute="_compute_closed")
    
    @api.depends('stage_id')
    def _compute_closed(self):
        for rec in self:
            if rec.stage_id and rec.stage_id.is_closed and self.user_has_groups('studio_customization.csr_6d5b6639-2e09-496d-b9c8-09a4d829f9bd'):
                rec.custom_is_closed = rec.stage_id.is_closed
            else:
                rec.custom_is_closed = False

    @api.depends('stage_id')
    def _compute_stage_id(self):
        for rec in self:
            if rec.stage_id:
                rec.state = rec.stage_id.name

    def _send_task_rating_mail(self, force_send):
        super(ProjectTask, self)._send_task_rating_mail(force_send=force_send)
        config_params = self.env['ir.config_parameter'].sudo()
        field_service_sms_policy_tasks = config_params.get_param('field_service_sms_policy_tasks')
        if field_service_sms_policy_tasks == 'per_order':
            sale_order_task = self.env['project.task'].search([('sale_order_id', '=', self.sale_order_id.id)])
            flag = True
            count = 0
            for task in sale_order_task:
                if task.sending_date == datetime.datetime.today().date():
                    flag = False
                else:
                    pass
                if task.sending_date == False:
                    count += 1

            if count == len(sale_order_task):
                service_template = self.env['project.service.template'].search(
                    [('project_id', '=', self.project_id.id),
                     ('service_product', '=', self.sale_line_id.product_id.product_tmpl_id.id)], limit=1)
                state_lines = []
                for state_line in service_template.template_details_lines:
                    state_lines.append(state_line.stage_id.name)
                for tasks in sale_order_task:
                    tasks.state_lines = state_lines
            lst_state_field = ast.literal_eval(self.state_lines)
            if flag or (self.stage_id.name in lst_state_field):
                if self.stage_id.name in lst_state_field:
                    lst_state_field.remove(self.stage_id.name)
                    for tasks in sale_order_task:
                        tasks.state_lines = lst_state_field
                self.sending_date = datetime.datetime.today().date()

                _logger.info('SMS:: function _send_task_rating_mail')
                survey_url = ''
                for rec in self:

                    self._get_custom_access_token()
                    service_template = self.env['project.service.template'].search(
                        [('project_id', '=', rec.project_id.id),
                        ('service_product', '=', rec.sale_line_id.product_id.product_tmpl_id.id)], limit=1)
                    _logger.info(f'SMS:: Project Service Template: {service_template}')

                    if service_template:
                        template_obj = service_template.template_details_lines.filtered(
                            lambda template_line:template_line.stage_id.id == rec.stage_id.id)
                        _logger.info(f'SMS:: Service Template Body: {template_obj}')
                        if template_obj:
                            if rec.stage_id.name == "Completed" and rec.custom_access_token:
                                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                survey_url = '\n\nSatisfaction Survey: ' + base_url + '/rate/' + str(rec.custom_access_token) + '/3'
                                message_body = template_obj.sms_template_id.body + ' ' + survey_url
                            else:
                                message_body = template_obj.sms_template_id.body
                            mobile = rec.sale_order_id.x_studio_contact_no_1
                            phone = rec.x_studio_contact_no
                            if not mobile and not phone:
                                raise UserError(_('There is no mobile number present in sale order or task. Please add to proceed.'))
                            mobile_number = mobile if mobile else phone
                            pattern = '(^[+63]{3})([0-9]{10})'
                            result = re.match(pattern, mobile_number)
                            if not result:
                                raise UserError(_('Contact number format is not accepted. You either have space between number '
                                                  'or phone number does not starts from +63'))
                            try:
                                sent = self.env['sms.api'].sudo()._send_sms(mobile_number, message_body)
                                _logger.info(f'SMS:: SMS sent successfully for {rec.stage_id.name} stage.')
                            except Exception as e:
                                _logger.error(f'SMS:: Error has encountered in sending SMS: {e}')
                    # Which will redirect to the current page
                    if rec.stage_id.name == "Completed":
                        return {
                            'type': 'ir.actions.act_url',
                            'url': survey_url,
                            'target': 'self',
                            'res_id': self.id,
                        }

        elif field_service_sms_policy_tasks == 'per_service_template':
            survey_url = ''
            sale_order_task = self.env['project.task'].search([('sale_order_id', '=', self.sale_order_id.id)])
            dict = {}
            sale_line_keys = {}
            for line in sale_order_task:
                dict[line.id] = line.sale_line_id.product_id.id
            for key, value in dict.items():
                if value in sale_line_keys:
                    sale_line_keys[value].append(key)
                else:
                    sale_line_keys[value] = [key]
            for key_item, value_item in sale_line_keys.items():
                if self.id in value_item:
                    flag = True
                    count = 0
                    for task_id in value_item:
                        task = self.browse(task_id)
                        if task.sending_date == datetime.datetime.today().date():
                            flag = False
                        else:
                            pass
                        if task.sending_date == False:
                            count += 1

                    if count == len(value_item):

                        service_template = self.env['project.service.template'].search(
                            [('project_id', '=', self.project_id.id),
                             ('service_product', '=', self.sale_line_id.product_id.product_tmpl_id.id)], limit=1)
                        state_lines = []
                        for state_line in service_template.template_details_lines:
                            state_lines.append(state_line.stage_id.name)
                        for task_id in value_item:
                            tasks = self.browse(task_id)
                            tasks.state_lines = state_lines
                    lst_state_field = ast.literal_eval(self.state_lines)

                    if flag or (self.stage_id.name in lst_state_field):
                        if self.stage_id.name in lst_state_field:
                            lst_state_field.remove(self.stage_id.name)
                            for tasks_id in value_item:
                                tasks = self.browse(tasks_id)
                                tasks.state_lines = lst_state_field

                        self.sending_date = datetime.datetime.today().date()

                        _logger.info('SMS:: function _send_task_rating_mail')
                        for rec in self:

                            self._get_custom_access_token()
                            service_template = self.env['project.service.template'].search(
                                [('project_id', '=', rec.project_id.id),
                                 ('service_product', '=', rec.sale_line_id.product_id.product_tmpl_id.id)], limit=1)
                            _logger.info(f'SMS:: Project Service Template: {service_template}')

                            if service_template:
                                template_obj = service_template.template_details_lines.filtered(
                                    lambda template_line: template_line.stage_id.id == rec.stage_id.id)
                                _logger.info(f'SMS:: Service Template Body: {template_obj}')
                                if template_obj:
                                    if rec.stage_id.name == "Completed" and rec.custom_access_token:
                                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                        survey_url = '\n\nSatisfaction Survey: ' + base_url + '/rate/' + str(
                                            rec.custom_access_token) + '/3'
                                        message_body = template_obj.sms_template_id.body + ' ' + survey_url
                                    else:
                                        message_body = template_obj.sms_template_id.body
                                    mobile = rec.sale_order_id.x_studio_contact_no_1
                                    phone = rec.x_studio_contact_no
                                    if not mobile and not phone:
                                        raise UserError(
                                            _('There is no mobile number present in sale order or task. Please add to proceed.'))
                                    mobile_number = mobile if mobile else phone
                                    pattern = '(^[+63]{3})([0-9]{10})'
                                    result = re.match(pattern, mobile_number)
                                    if not result:
                                        raise UserError(
                                            _('Contact number format is not accepted. You either have space between number '
                                              'or phone number does not starts from +63'))
                                    try:
                                        sent = self.env['sms.api'].sudo()._send_sms(mobile_number, message_body)
                                        _logger.info(f'SMS:: SMS sent successfully for {rec.stage_id.name} stage.')
                                    except Exception as e:
                                        _logger.error(f'SMS:: Error has encountered in sending SMS: {e}')
                            #Which will redirect to the current page
                            if rec.stage_id.name == "Completed":
                                return {
                                    'type': 'ir.actions.act_url',
                                    'url': survey_url,
                                    'target': 'self',
                                    'res_id': self.id,
                                }
