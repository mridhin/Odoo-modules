from odoo import fields, models, api, _
from odoo.exceptions import UserError,ValidationError
import requests
import time
import logging
import base64
import json
from datetime import datetime
from lxml import etree

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_lazada_product = fields.Boolean()
    updated_to_lazada = fields.Boolean()
    lazada_item_id = fields.Char('Lazada Item ID')
    lazada_update_time = fields.Datetime('Lazada Update Time')
    lazada_id = fields.Char('Lazada ID')
    lazada_shop_id = fields.Many2one('lazada.connector', string="Lazada Shop")
    lazada_seller_sku = fields.Char('Lazada Seller SKU')
    lazada_shop_sku = fields.Char('Lazada Shop SKU')
    lazada_category_id = fields.Many2one('lazada.category','Lazada Category')


    @api.constrains('weight', 'is_lazada_product','product_length','product_width','product_height','default_code')
    def _check_lazada_contrains(self):
        for product in self:
            if product.is_lazada_product and product.weight <= 0:
                raise ValidationError(
                    _('Weight should be more than 0 for Lazada Products'))
            if product.is_lazada_product and not product.default_code:
                raise ValidationError(
                    _('Please Enter Internal Reference'))
            if product.is_lazada_product and product.detailed_type == 'product' and product.product_length <= 0:
                raise ValidationError(
                    _('Length should be more than 0 for Lazada Products'))
            if product.is_lazada_product and product.detailed_type == 'product' and product.product_width <= 0:
                raise ValidationError(
                    _('Width should be more than 0 for Lazada Products'))
            if product.is_lazada_product and product.detailed_type == 'product' and product.product_height <= 0:
                raise ValidationError(
                    _('Height should be more than 0 for Lazada Products'))


class LazadaConnectorProduct(models.Model):
    _inherit = 'lazada.connector'

    def get_final_url(self, path, update_after, update_before, item_status, offset):
        secret = self.app_secret
        parameters = {
            'update_before': update_before,
            'update_after': update_after,
            'item_status': item_status,
            'offset': offset,
        }
        sign = self.sign(secret, api, parameters)
        ts = int(round(time.time() * 1000))
        timestamp = str(ts)
        app_key = self.app_key
        sign_method = 'sha256'
        access_token = self.access_token
        host = self.url

        url = host + path + "?timestamp=%s&app_key=%s&sign_method=%s&sign=%s&access_token=%s&filter=%s&update_before=%s&offset=%s&update_after=%s" % (
        timestamp, app_key, sign_method, sign, access_token, item_status, update_before, offset, update_after)
        return url

    def get_products_from_lazada_all(self, update_after, update_before, item_status):
        product_sync_completed = False
        offset = 0
        page_size = 10
        while not product_sync_completed:

            sync_status = self.get_products_from_lazada(offset, page_size, update_after, update_before, item_status)
            if sync_status == 'Completed':
                product_sync_completed = True
            else:
                offset += 10

    def get_products_from_lazada(self, offset, page_size, update_after, update_before, filter):
        ts = int(round(time.time() * 1000))
        api_method = "/products/get"
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'filter': filter})
        parameters.update({'offset': offset})
        parameters.update({'limit': 10})
        if update_before:
            parameters.update({'update_before': update_before.replace(microsecond=0).isoformat()})
        if update_after:
            parameters.update({'update_after': update_after.replace(microsecond=0).isoformat()})
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        # response = {
        #     "code": "0",
        #     "data": {
        #         "total_products": "10",
        #         "products": [{
        #             "created_time": "1611554725000",
        #             "updated_time": "1611554725000",
        #             "images": "[     \"https://my-live.slatic.net/p/540bc796d1eadf316018038d8840f20a.jpg\",     \"https://my-live.slatic.net/p/8913fc357e139ef78ad2f071e9586334.jpg\" ]",
        #             "skus": ["[ { \"Status\":\"active\", \"SkuId\": 314525867, \"quantity\":0, \"product_weight\":\"0.03\", \"Images\":[\"http://sg-live-01.slatic.net/p/BUYI1-catalog.jpg\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"], \"SellerSku\":\"39817:01:01\", \"ShopSku\":\"BU565ELAX8AGSGAMZ-1104491\", \"Url\":\"https://alice.lazada.sg/asd-1083832.html\", \"package_width\":\"10.00\", \"special_to_time\":\"2020-02-0300:00\", \"special_from_time\":\"2015-07-3100:00\", \"package_height\":\"4.00\", \"special_price\":9, \"price\":32, \"package_length\":\"10.00\", \"package_weight\":\"0.04\", \"Available\":0, \"special_to_date\":\"2020-02-03\" } ]", "[ { \"Status\":\"active\", \"SkuId\": 314525867, \"quantity\":0, \"product_weight\":\"0.03\", \"Images\":[\"http://sg-live-01.slatic.net/p/BUYI1-catalog.jpg\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"], \"SellerSku\":\"39817:01:01\", \"ShopSku\":\"BU565ELAX8AGSGAMZ-1104491\", \"Url\":\"https://alice.lazada.sg/asd-1083832.html\", \"package_width\":\"10.00\", \"special_to_time\":\"2020-02-0300:00\", \"special_from_time\":\"2015-07-3100:00\", \"package_height\":\"4.00\", \"special_price\":9, \"price\":32, \"package_length\":\"10.00\", \"package_weight\":\"0.04\", \"Available\":0, \"special_to_date\":\"2020-02-03\" } ]"],
        #             "item_id": "180226526",
        #             "suspendedSkus": [" \"suspendedSkus\":[{\"rejectReason\":\"Possible counterfeit. Please provide proof of authenticity in order to reactivate your product. Refer to this link for more info: https://goo.gl/YjeXER:null\", \"SellerSku\":\"2142206567-1640869121385-0\", \"SkuId\":12185089556}]", " \"suspendedSkus\":[{\"rejectReason\":\"Possible counterfeit. Please provide proof of authenticity in order to reactivate your product. Refer to this link for more info: https://goo.gl/YjeXER:null\", \"SellerSku\":\"2142206567-1640869121385-0\", \"SkuId\":12185089556}]"],
        #             "subStatus": "Lock,Reject,Live Reject,Admin",
        #             "trialProduct": "false",
        #             "rejectReason": ["[{\"suggestion\":\"\",\"violationDetail\":\"Wrong Description,Price Not Reasonable,Wrong Image, No White Background:Wrong image resolution\"}]", "[{\"suggestion\":\"\",\"violationDetail\":\"Wrong Description,Price Not Reasonable,Wrong Image, No White Background:Wrong image resolution\"}]"],
        #             "primary_category": "10000211",
        #             "marketImages": "[     \"https://my-live.slatic.net/p/540bc796d1eadf316018038d8840f20a.jpg\",     \"https://my-live.slatic.net/p/8913fc357e139ef78ad2f071e9586334.jpg\" ]",
        #             "attributes": "{           \"description\": \"\u003cp\u003easd\u003c/p\u003e\\n\",           \"name\": \"asd\",           \"brand\": \"Asante\",           \"short_description\": \"\u003cul\u003e\u003cli\u003easdasd\u003c/li\u003e\u003c/ul\u003e\",           \"warranty_type\": \"International Manufacturer\"}",
        #             "status": "Active,InActive,Pending QC,Suspended,Deleted"
        #         }, {
        #             "created_time": "1611554725000",
        #             "updated_time": "1611554725000",
        #             "images": "[     \"https://my-live.slatic.net/p/540bc796d1eadf316018038d8840f20a.jpg\",     \"https://my-live.slatic.net/p/8913fc357e139ef78ad2f071e9586334.jpg\" ]",
        #             "skus": ["[ { \"Status\":\"active\", \"SkuId\": 314525867, \"quantity\":0, \"product_weight\":\"0.03\", \"Images\":[\"http://sg-live-01.slatic.net/p/BUYI1-catalog.jpg\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"], \"SellerSku\":\"39817:01:01\", \"ShopSku\":\"BU565ELAX8AGSGAMZ-1104491\", \"Url\":\"https://alice.lazada.sg/asd-1083832.html\", \"package_width\":\"10.00\", \"special_to_time\":\"2020-02-0300:00\", \"special_from_time\":\"2015-07-3100:00\", \"package_height\":\"4.00\", \"special_price\":9, \"price\":32, \"package_length\":\"10.00\", \"package_weight\":\"0.04\", \"Available\":0, \"special_to_date\":\"2020-02-03\" } ]", "[ { \"Status\":\"active\", \"SkuId\": 314525867, \"quantity\":0, \"product_weight\":\"0.03\", \"Images\":[\"http://sg-live-01.slatic.net/p/BUYI1-catalog.jpg\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"], \"SellerSku\":\"39817:01:01\", \"ShopSku\":\"BU565ELAX8AGSGAMZ-1104491\", \"Url\":\"https://alice.lazada.sg/asd-1083832.html\", \"package_width\":\"10.00\", \"special_to_time\":\"2020-02-0300:00\", \"special_from_time\":\"2015-07-3100:00\", \"package_height\":\"4.00\", \"special_price\":9, \"price\":32, \"package_length\":\"10.00\", \"package_weight\":\"0.04\", \"Available\":0, \"special_to_date\":\"2020-02-03\" } ]"],
        #             "item_id": "180226526",
        #             "suspendedSkus": [" \"suspendedSkus\":[{\"rejectReason\":\"Possible counterfeit. Please provide proof of authenticity in order to reactivate your product. Refer to this link for more info: https://goo.gl/YjeXER:null\", \"SellerSku\":\"2142206567-1640869121385-0\", \"SkuId\":12185089556}]", " \"suspendedSkus\":[{\"rejectReason\":\"Possible counterfeit. Please provide proof of authenticity in order to reactivate your product. Refer to this link for more info: https://goo.gl/YjeXER:null\", \"SellerSku\":\"2142206567-1640869121385-0\", \"SkuId\":12185089556}]"],
        #             "subStatus": "Lock,Reject,Live Reject,Admin",
        #             "trialProduct": "false",
        #             "rejectReason": ["[{\"suggestion\":\"\",\"violationDetail\":\"Wrong Description,Price Not Reasonable,Wrong Image, No White Background:Wrong image resolution\"}]", "[{\"suggestion\":\"\",\"violationDetail\":\"Wrong Description,Price Not Reasonable,Wrong Image, No White Background:Wrong image resolution\"}]"],
        #             "primary_category": "10000211",
        #             "marketImages": "[     \"https://my-live.slatic.net/p/540bc796d1eadf316018038d8840f20a.jpg\",     \"https://my-live.slatic.net/p/8913fc357e139ef78ad2f071e9586334.jpg\" ]",
        #             "attributes": "{           \"description\": \"\u003cp\u003easd\u003c/p\u003e\\n\",           \"name\": \"asd\",           \"brand\": \"Asante\",           \"short_description\": \"\u003cul\u003e\u003cli\u003easdasd\u003c/li\u003e\u003c/ul\u003e\",           \"warranty_type\": \"International Manufacturer\"}",
        #             "status": "Active,InActive,Pending QC,Suspended,Deleted"
        #         }]
        #     },
        #     "request_id": "0ba2887315178178017221014"
        # }
        if response.get('data', False) and response.get('data').get('products', False):
            print('cominassssssssssg')
            sync_status = 'Not completed'
            for product in response.get('data').get('products'):
                self.create_product_based_on_data(product)
        sync_status = 'Completed'  # Need to update the status based on response, if it has equal to 10, then it should return not completed
        return sync_status

    def get_products(self, item_list):
        for product in item_list:
            attributes = product.get('attributes', False)
            product_vals = {}
            product_varis = product.get('skus', [])
            if product_varis:
                for sku in product_varis:
                    print(sku['quantity'])
                    # continue
                    product_tmpl_id = self.env['product.template'].search(
                        [('lazada_item_id', '=', str(product.get('item_id', False))),
                         ('default_code', '=', sku.get('SellerSku', False))], limit=1)
                    if not product_tmpl_id:
                        product_tmpl_id = self.env['product.template'].search(
                            [('default_code', '=', sku.get('SellerSku', False))], limit=1)

                    skus_vals = {
                        'price': sku['price'],
                        'SellerSku': sku['SellerSku'],
                        'ShopSku': sku['ShopSku'],
                        'quantity': sku['quantity'],
                        'package_weight': sku['package_weight'],
                        'package_width': sku['package_width'],
                        'package_height': sku['package_height'],
                        'package_length': sku['package_length'],
                        '_compatible_variation_': sku.get('_compatible_variation_', ""),
                    }
                    images = sku.get('images')
                    images = json.loads(images)
                    if "http://" in images[0] or "https://" in images[0]:
                        image = base64.b64encode(requests.get(images[0]).content)

                    product_vals = {
                        "list_price": skus_vals.get('price'),
                        "name": attributes.get('name', False),
                        'lazada_description': attributes.get('short_description', '<p></p>'),
                        'lazada_long_description': attributes.get('description', '<p></p>'),
                        "lazada_default_code": skus_vals.get('ShopSku'),
                        "lazada_seller_sku": skus_vals.get('SellerSku'),
                        "lazada_credential_id": self.id,

                        "weight": skus_vals.get('package_weight'),
                        "product_width": skus_vals.get('package_width'),
                        "product_height": skus_vals.get('package_height'),
                        "product_length": skus_vals.get('package_length'),
                        "image_1920": image,
                    }
                    if product_tmpl_id:

                        product_product_id = product_tmpl_id.write(product_vals)
                    else:
                        product_vals.update({
                            'default_code': skus_vals.get('SellerSku'),
                            'type': 'product',
                            'lazada_item_id': product.get('item_id', False),

                        })
                        product_tmpl_id = [self.env['product.template'].create(product_vals)]
                    _logger.info(product_tmpl_id)


    def product_notification(self, post_val):
        data = post_val.get('data')
        lazada_item_id = data.get('item_id')
        self.get_product_by_lazada_id(lazada_item_id)
        return True #It can be updated based on needed response



    def get_product_by_lazada_id(self,lazada_item_id=False,sku=False):
        ts = int(round(time.time() * 1000))
        api_method = "/product/item/get"
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        if lazada_item_id:
            parameters.update({'item_id': lazada_item_id})
        elif sku:
            parameters.update({'seller_sku': sku})
        else:
            raise UserError('Please pass either lazada item id or sku')
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        # response = {
        #     "code": "0",
        #     "data": {
        #         "created_time": "1611554725000",
        #         "updated_time": "1611554725000",
        #         "images": "[     \"https://my-live.slatic.net/p/540bc796d1eadf316018038d8840f20a.jpg\",     \"https://my-live.slatic.net/p/8913fc357e139ef78ad2f071e9586334.jpg\" ]",
        #         "skus": ["[     {         \"Status\": \"active\",         \"SkuId\": 314525867,         \"quantity\": 0,         \"product_weight\": \"0.03\",         \"Images\": [             \"http://sg-live-01.slatic.net/p/BUYI1-catalog.jpg\",             \"\",             \"\",             \"\",             \"\",             \"\",             \"\",             \"\"         ],         \"SellerSku\": \"39817:01:01\",         \"ShopSku\": \"BU565ELAX8AGSGAMZ-1104491\",         \"Url\": \"https://alice.lazada.sg/asd-1083832.html\",         \"package_width\": \"10.00\",         \"special_to_time\": \"2020-02-0300:00\",         \"special_from_time\": \"2015-07-3100:00\",         \"package_height\": \"4.00\",         \"special_price\": 9,         \"price\": 32,         \"package_length\": \"10.00\",         \"package_weight\": \"0.04\",         \"Available\": 0,         \"special_to_date\": \"2020-02-03\",         \"multiWarehouseInventories\":[          {              \"warehouseCode\":\"warehouseTest1\",              \"quantity\": 20          },         {              \"warehouseCode\":\"warehouseTest2\",              \"quantity\": 30          }         ]     } ]", "[     {         \"Status\": \"active\",         \"SkuId\": 314525867,         \"quantity\": 0,         \"product_weight\": \"0.03\",         \"Images\": [             \"http://sg-live-01.slatic.net/p/BUYI1-catalog.jpg\",             \"\",             \"\",             \"\",             \"\",             \"\",             \"\",             \"\"         ],         \"SellerSku\": \"39817:01:01\",         \"ShopSku\": \"BU565ELAX8AGSGAMZ-1104491\",         \"Url\": \"https://alice.lazada.sg/asd-1083832.html\",         \"package_width\": \"10.00\",         \"special_to_time\": \"2020-02-0300:00\",         \"special_from_time\": \"2015-07-3100:00\",         \"package_height\": \"4.00\",         \"special_price\": 9,         \"price\": 32,         \"package_length\": \"10.00\",         \"package_weight\": \"0.04\",         \"Available\": 0,         \"special_to_date\": \"2020-02-03\",         \"multiWarehouseInventories\":[          {              \"warehouseCode\":\"warehouseTest1\",              \"quantity\": 20          },         {              \"warehouseCode\":\"warehouseTest2\",              \"quantity\": 30          }         ]     } ]"],
        #         "item_id": "234222211",
        #         "suspendedSkus": [" \"suspendedSkus\":[{\"rejectReason\":\"Possible counterfeit. Please provide proof of authenticity in order to reactivate your product. Refer to this link for more info: https://goo.gl/YjeXER:null\", \"SellerSku\":\"2142206567-1640869121385-0\", \"SkuId\":12185089556}]", " \"suspendedSkus\":[{\"rejectReason\":\"Possible counterfeit. Please provide proof of authenticity in order to reactivate your product. Refer to this link for more info: https://goo.gl/YjeXER:null\", \"SellerSku\":\"2142206567-1640869121385-0\", \"SkuId\":12185089556}]"],
        #         "subStatus": "Lock,Reject,Live_Reject,Admin",
        #         "variation": {
        #             "variation3": {
        #                 "has_image": "false",
        #                 "name": "Volume",
        #                 "options": ["100ml", "100ml"],
        #                 "label": "color",
        #                 "customize": "false"
        #             },
        #             "variation4": {
        #                 "has_image": "false",
        #                 "name": "Size",
        #                 "options": ["m", "m"],
        #                 "label": "color",
        #                 "customize": "false"
        #             },
        #             "variation1": {
        #                 "has_image": "red",
        #                 "name": "color_family",
        #                 "options": ["false", "false"],
        #                 "label": "color",
        #                 "customize": "true"
        #             },
        #             "variation2": {
        #                 "has_image": "false",
        #                 "name": "SizeX",
        #                 "options": ["ss", "ss"],
        #                 "label": "color",
        #                 "customize": "true"
        #             }
        #         },
        #         "trialProduct": "true,false",
        #         "rejectReason": ["[{\"suggestion\":\"\",\"violationDetail\":\"Wrong Description,Price Not Reasonable,Wrong Image, No White Background:Wrong image resolution\"}]", "[{\"suggestion\":\"\",\"violationDetail\":\"Wrong Description,Price Not Reasonable,Wrong Image, No White Background:Wrong image resolution\"}]"],
        #         "primary_category": "10000211",
        #         "marketImages": "[     \"https://my-live.slatic.net/p/540bc796d1eadf316018038d8840f20a.jpg\",     \"https://my-live.slatic.net/p/8913fc357e139ef78ad2f071e9586334.jpg\" ]",
        #         "attributes": "{ \"description\": \"\u003cp\u003easd\u003c/p\u003e\\n\",           \"name\": \"asd\",           \"brand\": \"Asante\",           \"short_description\": \"\u003cul\u003e\u003cli\u003easdasd\u003c/li\u003e\u003c/ul\u003e\",           \"warranty_type\": \"International Manufacturer\"}",
        #         "status": "Active,InActive,Pending QC,Suspended,Deleted"
        #     },
        #     "request_id": "0ba2887315178178017221014"
        # }
        data = response.get('data')
        self.create_product_based_on_data(data)

    def create_product_based_on_data(self, product):
        attributes = product.get('attributes', False)
        # attributes = json.loads(attributes)
        product_vals = {}
        lazada_item_id = product.get('item_id')
        product_varis = product.get('skus', [])
        if product_varis:
            for sku in product_varis:
                # sku = json.loads(sku)
                # sku = sku[0]  # Check and update according to data
                product_tmpl_id = self.env['product.template'].search(
                    [('lazada_item_id', '=', str(product.get('item_id', False))),
                     ('default_code', '=', sku.get('SellerSku', False))], limit=1)
                if not product_tmpl_id:
                    product_tmpl_id = self.env['product.template'].search(
                        [('default_code', '=', sku.get('SellerSku', False))], limit=1)
                skus_vals = {
                    'price': sku['price'],
                    'SellerSku': sku['SellerSku'],
                    'ShopSku': sku['ShopSku'],
                    'quantity': sku['quantity'],
                    'package_weight': sku['package_weight'],
                    'package_width': sku['package_width'],
                    'package_height': sku['package_height'],
                    'package_length': sku['package_length'],
                    'Images': product['images'],
                    '_compatible_variation_': sku.get('_compatible_variation_', ""),
                }
                image = ""
                if skus_vals.get('Images', False):
                    images = skus_vals.get('Images')[0]
                    # images = json.loads(images)
                    if "http://" in images or "https://" in images:
                        image = base64.b64encode(requests.get(images).content)
                product_vals = {
                    'lazada_item_id': lazada_item_id,
                    'name': attributes.get('name'),
                    'lazada_shop_id': self.id,
                    'is_lazada_product': True,
                    'lazada_update_time': datetime.now(),
                    'description_sale': attributes.get('description'),
                    'image_1920': image,
                    "list_price": skus_vals.get('price'),
                    "name": attributes.get('name', False),
                    # 'lazada_long_description': attributes.get('description', '<p></p>'),
                    "default_code": skus_vals.get('SellerSku'),
                    "weight": skus_vals.get('package_weight'),
                    "product_width": skus_vals.get('package_width'),
                    "product_height": skus_vals.get('package_height'),
                    "product_length": skus_vals.get('package_length'),
                }
                brand = attributes.get('brand')
                print(brand)
                if brand:
                    product_brand = self.env['product.brand'].search([('name','=',brand)])
                    if not product_brand:
                        product_brand = self.env['product.brand'].create({'name':brand})
                    product_vals['product_brand_id'] =  product_brand.id
                if product_tmpl_id:
                    product_product_id = product_tmpl_id.write(product_vals)
                else:
                    product_vals.update({
                        'default_code': skus_vals.get('SellerSku'),
                        'type': 'product',
                        'lazada_item_id': product.get('item_id', False),

                    })
                    product_tmpl_id = [self.env['product.template'].create(product_vals)]
                _logger.info(product_tmpl_id)

    def products_from_odoo_to_lazada(self):
        odoo_products = self.env['product.product'].search([('is_lazada_product','=',True),'|',('lazada_item_id','=',''),('lazada_item_id','=',False)])
        for product in odoo_products:
            root = etree.Element("Request")
            product_element = etree.SubElement(root, 'Product')
            primary_category = etree.SubElement(product_element, 'PrimaryCategory')
            if product.lazada_category_id:
                primary_category.text = str(product.lazada_category_id.lazada_category_id)
            else:
                raise UserError("Please select lazada category for "+str(product.name))


            #########As of now image functionality has hidden, but later we can do it#######
            # # print(product.image_1920)
            # # image_response = self.upload_image(product.image_1920)
            # # print(image_response)
            # if not product.image_1920:
            #     raise UserError('Please upload image for '+str(product.name)+'. Product image should be minimim 320*320 size.')
            #
            image_url = False
            #
            # images = etree.SubElement(root, 'Images')
            # image_url_response = self.upload_image_url('https://sandbox-ecommerce-staging.odoo.com/web/image?model=product.product&id=22&field=image_1920')
            # image_url_response = self.upload_image_url('https://lzd-img-global.slatic.net/g/p/3aa895bd0665e2be8b16b264dafcfdc8.jpg')
            #
            # print(image_url_response)
            # image_url = image_url_response.get('data').get('image').get('url')
            # print(image_url)
            # ########As of now image functionality has hidden, but later we can do it#######
            #
            image_url = "https://ph-live-02.slatic.net/p/3aa895bd0665e2be8b16b264dafcfdc8.jpg"
            if image_url:
                images_element = etree.SubElement(product_element, 'Images')
                images_element_image = etree.SubElement(images_element, "Image")
                images_element_image.text = image_url

            attributes_element = etree.SubElement(product_element, 'Attributes')

            attributes_name_element = etree.SubElement(attributes_element, 'name')
            attributes_name_element.text = product.name

            if product.description_sale:
                attributes_description_element = etree.SubElement(attributes_element, 'description')
                attributes_description_element.text = product.description_sale

            attributes_brand_id_element = etree.SubElement(attributes_element, 'brand_id')
            if product.product_brand_id:
                attributes_brand_id_element.text = str(product.product_brand_id.lazada_brand_id)
            else:
                raise UserError("Please select lazada brand for " + str(product.name))

            # attributes_brand_id_element.text = '40516'
            skus_element = etree.SubElement(product_element, 'Skus')
            skus_element_sku = etree.SubElement(skus_element, "Sku")
            skus_element_seller_sku = etree.SubElement(skus_element_sku, 'SellerSku')
            skus_element_seller_sku.text = product.default_code
            skus_element_price = etree.SubElement(skus_element_sku, 'price')
            skus_element_price.text = str(product.list_price)
            skus_element_package_height = etree.SubElement(skus_element_sku, 'package_height')
            skus_element_package_height.text = str(product.product_height)
            skus_element_package_length = etree.SubElement(skus_element_sku, 'package_length')
            skus_element_package_length.text = str(product.product_length)
            skus_element_package_width = etree.SubElement(skus_element_sku, 'package_width')
            skus_element_package_width.text = str(product.product_width)
            skus_element_package_weight = etree.SubElement(skus_element_sku, 'package_weight')
            skus_element_package_weight.text = str(product.weight)
            xml_request = etree.tostring(root, encoding='UTF-8')

            api_method = "/product/create"
            payload = xml_request.decode('utf-8')
            response = self.final_payload_response(api_method, payload)
            if response.get('data') and response.get('data').get('item_id'):
                data = response.get('data')
                item_id = data.get('item_id')
                for sku_list in data.get('sku_list'):
                    shop_sku = sku_list.get('shop_sku')
                    product.write({
                        'lazada_item_id': item_id,
                        'lazada_shop_sku': shop_sku
                    })
                self.env.cr.commit()
            else:
                raise UserError(response.get('detail')[0].get('message'))







