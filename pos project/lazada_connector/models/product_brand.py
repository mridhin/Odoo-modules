from odoo import fields, models, api
import time
import requests
import logging
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class ProductBranch(models.Model):
    _inherit = 'product.brand'

    lazada_brand_id = fields.Char()

class LazadaConnectorProductCategory(models.Model):
    _inherit = 'lazada.connector'

    def get_brands(self,lazada_item_id=False,sku=False):
        sync_completed = False
        offset = 0
        page_size = 200
        while not sync_completed:

            sync_status = self.get_brands_from_lazada(offset, page_size)
            if sync_status == 'Completed':
                sync_completed = True
            else:
                offset += 200
    def get_brands_from_lazada(self, offset, page_size):
        ts = int(round(time.time() * 1000))
        api_method = "/category/brands/query"
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'startRow': str(offset)})
        parameters.update({'pageSize': str(page_size)})
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        if response.get('data'):
            data = response.get('data')
            self.create_brands(data.get('module'))
            start_row = data.get('start_row') + 200
            total_record = data.get('total_record')
            print(start_row)
            print(total_record)
            if start_row >= total_record:
                return "Completed"
            else:
                return "Not Completed"
        else:
            raise ValidationError(response.get('message'))

    def create_brands(self, data):
        for datum in data:
            product_brand = self.env['product.brand'].search([('lazada_brand_id','=',datum.get('brand_id'))])
            if not product_brand:
                brand_vals = {
                    'name':datum.get('name'),
                    'lazada_brand_id':datum.get('brand_id'),
                }
                self.env['product.brand'].create(brand_vals)