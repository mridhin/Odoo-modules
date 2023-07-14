from odoo import api, models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        for task, users in users_per_task.items():
            if not users:
                continue
            for user in users:
                phone_number = user.partner_id.mobile
                if phone_number:
                    self.env['sms.api'].sudo()._send_sms(
                        [phone_number], ("Your have assigned to task %s", task._notify_get_action_link('view'))
                    )

        return super(ProjectTask, self)._task_message_auto_subscribe_notify(users_per_task)

