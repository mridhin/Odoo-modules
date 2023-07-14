from odoo import fields, models, api
import time
import requests
import logging


_logger = logging.getLogger(__name__)

class LazadaCategory(models.Model):
    _name = 'lazada.category'
    _description = 'Lazada Categories'
    _rec_name = 'complete_name'

    name = fields.Char()
    lazada_category_id = fields.Integer('Lazada Category Id')
    parent_id = fields.Many2one('lazada.category')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

class LazadaConnectorProductCategory(models.Model):
    _inherit = 'lazada.connector'

    def get_categories(self,lazada_item_id=False,sku=False):
        ts = int(round(time.time() * 1000))
        api_method = "/category/tree/get"
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        # print(response)
        if response.get('data'):
            data = response.get('data')
            for datum in data:
                self.create_child_catogories(datum)

    def create_child_catogories(self, data, parent_category = False):

        if data.get('children'):
            for datum in data.get('children'):
            #     # print(datum)
            #     # print("\n" * 4)
            #     parent_category = self.create_update_lazada_category(datum.get('name'),datum.get('category_id'),parent_category)
                self.create_child_catogories(datum)
        else:
            self.create_update_lazada_category(data.get('name'), data.get('category_id'), parent_category)

    def create_update_lazada_category(self, name, category_id, parent_category):
        vals = {
            'name': name,
            'lazada_category_id': category_id,
        }
        if parent_category:
            vals['parent_id'] = parent_category.id
        rec = self.env['lazada.category'].search([('lazada_category_id','=',category_id)])
        if not rec:
            return self.env['lazada.category'].create(vals)



