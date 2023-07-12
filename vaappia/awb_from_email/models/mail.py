from odoo import fields, models, api


class Mail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        # It overrides all from emails
        if values.get('email_from') is not None:
            config = self.env['ir.config_parameter'].sudo()
            awb_from_email = config.get_param('awb_from_email', default=False)
            if awb_from_email:
                values['email_from'] = awb_from_email
        res = super(Mail, self).create(values)
        return res
