from odoo import api, models, exceptions, fields
from odoo.exceptions import ValidationError
import requests
import base64

class SMSTemplate(models.Model):
    _inherit = "sms.template"

    active = fields.Boolean(string = "Active", default=True)

class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'
    @api.model
    def _send_sms(self, numbers, message):
        """ Send a single message to several numbers
        :param numbers: list of E164 formatted phone numbers
        :param message: content to send
        :raises ? TDE FIXME
        """
        config = self.env['ir.config_parameter'].sudo()
        sms_gateway_name = config.get_param('sms_gateway_name', default=False)
        print(sms_gateway_name)

        if sms_gateway_name and sms_gateway_name == 'smart_gateway':
            params = {
                'numbers': numbers,
                'message': message,
            }
            return self._awb_send_smart_sms(params)
        else:
            return super(SmsApi, self)._send_sms(numbers,message)

        # can't find where this function called
        # return self._contact_iap('/iap/message_send', params)
        # raise AccessDenied('You cannot use this SMS function. Error code: AWBSMS1')

    def _awb_send_smart_sms(self,message):
        config_params = self.env['ir.config_parameter'].sudo()
        smart_gateway_url = config_params.get_param('smart_gateway_url')
        smart_gateway_username = config_params.get_param('smart_gateway_username')
        smart_gateway_password = config_params.get_param('smart_gateway_password')
        print(smart_gateway_url)
        print(smart_gateway_username)
        print(smart_gateway_password)
        if smart_gateway_url and smart_gateway_username and smart_gateway_password:
            credentials = smart_gateway_username + ":" + smart_gateway_password
            credentials_bytes = credentials.encode('ascii')
            base64_bytes = base64.b64encode(credentials_bytes)
            base64_string = base64_bytes.decode('ascii')
            print(base64_string)
            headers = {"Authorization": "Basic " + base64_string}
            url = smart_gateway_url

            number = message.get('numbers')
            content = message.get('message')
            data = {
                'messageType':'sms',
                'destination': number,
                'text': content,
            }
            print(url)
            print(headers)
            print(data)
            response = requests.post(url, headers=headers, json=data)
            print(response)
            response_json = response.json()
            print(response_json)
            if response_json.get('id'):
                return [{'res_id': message.get('res_id'), 'state': 'success'}]
                # return [{'res_id':]
            else:
                # FIXME: Need to update below responses based on response from API, also the sms.sms failure type value according to that
                message = response_json.get('errorDescription')
                reason = 'sms_credit' if message == 'insufficient credits' else 'sms_server'
                self.env['sms.sms'].sudo().create({
                    'number': number,
                    'body': content,
                    'state': 'error',
                    'failure_type': reason
                })
                e_class = exceptions.UserError
                e = e_class(message)
                e.data = message
                raise e
        else:
            raise ValidationError('Please enter credentials for Smart Gateways')


    @api.model
    def _send_sms_batch(self, messages):
        """ Send SMS using IAP in batch mode
        :param messages: list of SMS to send, structured as dict [{
            'res_id':  integer: ID of sms.sms,
            'number':  string: E164 formatted phone number,
            'content': string: content to send
        }]
        :return: return of /iap/sms/1/send controller which is a list of dict [{
            'res_id': integer: ID of sms.sms,
            'state':  string: 'insufficient_credit' or 'wrong_number_format' or 'success',
            'credit': integer: number of credits spent to send this SMS,
        }]
        :raises: normally none
        """
        params = {
            'messages': messages
        }
        config = self.env['ir.config_parameter'].sudo()
        sms_gateway_name = config.get_param('sms_gateway_name', default=False)
        if sms_gateway_name and sms_gateway_name == 'smart_gateway':
            # stop
            return self._awb_send_smart_sms_batch(params)
        else:
            return super(SmsApi, self)._send_sms_batch(messages)

    def _awb_send_smart_sms_batch(self, params):
        config_params = self.env['ir.config_parameter'].sudo()
        smart_gateway_url = config_params.get_param('smart_gateway_url')
        smart_gateway_username = config_params.get_param('smart_gateway_username')
        smart_gateway_password = config_params.get_param('smart_gateway_password')
        if smart_gateway_url and smart_gateway_username and smart_gateway_password:
            credentials = smart_gateway_username + ":" + smart_gateway_password
            credentials_bytes = credentials.encode('ascii')
            base64_bytes = base64.b64encode(credentials_bytes)
            base64_string = base64_bytes.decode('ascii')
            headers = {"Authorization": "Basic "+base64_string}
            url = smart_gateway_url
            messages = params.get('messages')
            for message in messages:
                number = message.get('number')
                content = message.get('content')
                data = {
                    'messageType': 'sms',
                    'destination':number,
                    'text':content,
                }
                print(url)
                print(headers)
                print(data)
                response = requests.post(url, headers=headers, json=data)
                print(response)
                response_json = response.json()
                print(response_json)
                if response_json.get('id'):
                    return [{'res_id': message.get('res_id'), 'state': 'success'}]
                    # return [{'res_id':]
                else:
                    # FIXME: Need to update below responses based on response from API, also the sms.sms failure type value according to that
                    message = response_json.get('errorDescription')
                    reason = 'sms_credit' if message == 'insufficient credits' else 'sms_server'
                    self.env['sms.sms'].sudo().create({
                        'number': number,
                        'body': content,
                        'state': 'error',
                        'failure_type': reason
                    })
                    e_class = exceptions.UserError
                    e = e_class(message)
                    e.data = message
                    raise e
        else:
            raise ValidationError('Please enter credentials for Smart Gateways')