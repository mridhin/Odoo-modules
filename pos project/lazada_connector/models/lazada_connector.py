from odoo import fields, models, api, _
import requests
import hashlib
import time
import hmac
from lxml import etree
import logging

_logger = logging.getLogger(__name__)

class LazadaConnector(models.Model):
    _name = 'lazada.connector'
    _inherit = 'mail.thread'
    _rec_name = 'app_name'
    _description = 'Lazada Connector'

    tracking=True

    app_name = fields.Char(string='App Name', required=True, tracking=True)
    url = fields.Char(string='API URL', tracking=True, required=True)
    redirect_url = fields.Char(string='Redirect URL', tracking=True, required=True)
    mode = fields.Selection(
        string='Mode',
        selection=[('sandbox', 'Sandbox'),
                   ('production', 'Production'), ],
        required=True, default='sandbox' )

    app_key = fields.Char(string='App Key', tracking=True, required=True)
    app_secret = fields.Char(string='App Secret', tracking=True, required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('connection', 'Connection')],string='State', default='draft', tracking=True)
    access_token = fields.Char('Access Token', tracking=True)
    refresh_token = fields.Char('Refresh Token', tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users','Sales Person', required=True)

    def action_connection(self):
        app_key = self.app_key
        redirect_url = self.redirect_url

        url = "https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri=%s&client_id=%s" % (redirect_url, app_key)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
        }

    def refresh_access_token(self):
        print(self)
        ts = int(round(time.time() * 1000))
        api_method = "/auth/token/refresh"
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'refresh_token': self.refresh_token})
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        json_response = r.json()
        print(json_response)
        access_token = json_response.get('access_token')
        refresh_token = json_response.get('refresh_token')
        self.write({'access_token': access_token, 'refresh_token': refresh_token, 'state': 'connection'})

    def draft_reset(self):
        for record in self:
            record.state = 'draft'

    def sign(self,secret, api, parameters):
        # ===========================================================================
        # @param secret
        # @param parameters
        # ===========================================================================
        sort_dict = sorted(parameters)

        parameters_str = "%s%s" % (api,
                                   str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

        h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"), digestmod=hashlib.sha256)

        return h.hexdigest().upper()

    def api_final_url(self, api, parameters, sign):
        # ===========================================================================
        # @param secret
        # @param parameters
        # Parameters are input from the filter and credentials. It is common functionality
        # ===========================================================================
        sort_dict = sorted(parameters)
        api_url = self.url
        parameters_str = "%s%s?%ssign=%s" % (api_url, api,
                                             str().join('%s=%s&' % (key, parameters[key]) for key in sort_dict), sign)
        return parameters_str

    def upload_image_url(self, url):
        root = etree.Element("Request")
        image_element = etree.SubElement(root, 'Image')
        image_element_url = etree.SubElement(image_element, 'Url')
        image_element_url.text = url
        xml_request = etree.tostring(root, encoding='UTF-8')
        api_method = "/image/migrate"
        payload = xml_request.decode('utf-8')
        return self.final_payload_response(api_method, payload)

    def final_payload_response(self,api_method,payload):
        ts = int(round(time.time() * 1000))
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'payload': payload})
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.post(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        print(response)
        return response


