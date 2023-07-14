from odoo import api, fields, models,_

import time
import requests
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_lazada_order = fields.Boolean()
    lazada_order_id = fields.Char('lazada Order ID')
    lazada_order_number = fields.Char('lazada Order Number')
    lazada_id = fields.Char('lazada ID')
    lazada_status = fields.Char('lazada Status')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lazada_order_line_id = fields.Char('lazada Order Line ID')



class LazadaConnectorOrder(models.Model):
    _inherit = 'lazada.connector'


    def get_orders_notification(self, post_val):
        # post_val = {
        #      "seller_id":"1234567",  #seller Id
        #      "message_type":0,
        #        "data":{
        #           "order_status":"unpaid", #Order Status
        #           "trade_order_id":"260422900198363", #trade order Id
        #           "trade_order_line_id":"260422900298363", #sub order Id
        #           "status_update_time":1603698638 #update time (seconds)
        #        },
        #        "timestamp":1603766859530, #time when notify(seconds)
        #        "site":"lazada_vn" #site
        #     }
        data = post_val.get('data')
        order_id = data.get('trade_order_id')
        self.get_order_details(order_id)

    def get_order_details(self, order_id):
        ts = int(round(time.time() * 1000))
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'order_id': order_id})
        api_method = "/order/get"
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        # response = {  "code": "0",  "data": {    "voucher": "0.00",    "warehouse_code": "dropshipping",    "order_number": "300034416",    "created_at": "2014-10-15 18:36:05 +0800",    "voucher_code": "3432",    "gift_option": "0",    "shipping_fee_discount_platform": "0.00",    "customer_last_name": "last_name",    "updated_at": "2014-10-15 18:36:05 +0800",    "promised_shipping_times": "2017-03-24 16:09:22",    "price": "99.00",    "national_registration_number": "1123",    "shipping_fee_original": "0.00",    "payment_method": "COD",    "customer_first_name": "First Name",    "shipping_fee_discount_seller": "0.00",    "shipping_fee": "0.00",    "branch_number": "2222",    "tax_code": "1234",    "items_count": "1",    "delivery_info": "1",    "statuses": [      "delivered",      "delivered"    ],    "address_billing": {      "country": "Singapore",      "address3": "address3",      "address2": "address2",      "city": "Singapore-Central",      "phone": "81***8",      "address1": "22 leonie hill road, #13-01",      "post_code": "239195",      "phone2": "24***22",      "last_name": "Last Name",      "address5": "address5",      "address4": "address4",      "first_name": "First Name"    },    "extra_attributes": "{\"TaxInvoiceRequested\":\"true\"}",    "order_id": "16090",    "gift_message": "Gift",    "remarks": "remarks",    "address_shipping": {      "country": "Singapore",      "address3": "address3",      "address2": "address2",      "city": "Singapore-Central",      "phone": "94236248",      "address1": "318 tanglin road, phoenix park, #01-59",      "post_code": "247979",      "phone2": "1******2",      "last_name": "Last Name",      "address5": "1******2",      "address4": "address4",      "first_name": "First Name"    }  },  "request_id": "0ba2887315178178017221014"}
        if response.get('data'):
            self.create_update_orders(response.get('data'))
        else:
            raise ValidationError(response.get('message'))

    def create_update_orders(self,data):
        print(data)
        # stop
        order_number = data.get('order_number')
        order_id = data.get('order_id')
        sale_order = self.env['sale.order'].search([('lazada_order_id','=',order_id)])
        statuses = data.get('statuses')
        date_order = data.get('created_at')
        lazada_status = ''
        if statuses:
            lazada_status = statuses[0]

        print(sale_order)
        if sale_order:
            if statuses:
                sale_order.write({'lazada_status':lazada_status})
        else:
            name = data.get('customer_first_name', '')
            if data.get('customer_last_name'):
                name += ' ' + data.get('customer_last_name', '')
            partner_id = False

            if data.get('address_billing'):
                address_billing = data.get('address_billing')
                partner_id = self.get_partner_details(address_billing,name,'customer')
                invoice_partner_id = self.get_partner_details(address_billing,name,'invoice',partner_id)


                _logger.info(partner_id)

            if data.get('address_shipping'):
                delivery_partner_id = self.get_partner_details(address_billing, name, 'delivery',partner_id)

            sale_order_val = {
                'partner_id': partner_id.id,
                "partner_invoice_id": invoice_partner_id.id,
                "partner_shipping_id": delivery_partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                'warehouse_id': self.warehouse_id.id,
                'date_order': date_order[:-6],
                'is_lazada_order': True,
                'lazada_order_number': order_number,
                'lazada_order_id': order_id,
                'lazada_id': self.id,
                'lazada_status': lazada_status,
                'user_id':self.user_id.id
            }
            sale_order = self.env['sale.order'].create(sale_order_val)
            if sale_order:
                self.create_order_line(order_id,sale_order)
            # stop
    def create_order_line(self,order_id,sale_order):
        ts = int(round(time.time() * 1000))
        api_method = "/orders/items/get"
        order_ids = [order_id]
        _logger.info(order_ids)
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'order_ids': order_ids})
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        print(response)
        # response = {
        #             "code": "0",
        #             "data": [{
        #                 "pick_up_store_info": {
        #                     "pick_up_store_address": "Ali Center, Shenzhen",
        #                     "pick_up_store_name": "Alibaba",
        #                     "pick_up_store_open_hour": ["[\"Sunday 9:00-18:00\", \"Mondday,Tuesday,Wendnesday,Thursday,Friday 8:00-20:00\"]", "[\"Sunday 9:00-18:00\", \"Mondday,Tuesday,Wendnesday,Thursday,Friday 8:00-20:00\"]"],
        #                     "pick_up_store_code": "d4b04804-9192-4a8c-8ed1-5ebcd7d3c067"
        #                 },
        #                 "tax_amount": "6.48",
        #                 "reason": "reason",
        #                 "sla_time_stamp": "2019-06-24T23:59:59+08:00",
        #                 "voucher_seller": "0.00",
        #                 "purchase_order_id": "3454",
        #                 "voucher_code_seller": "X234",
        #                 "voucher_code": "X3453",
        #                 "package_id": "345",
        #                 "buyer_id": "1001",
        #                 "variation": "1",
        #                 "product_id": "12345",
        #                 "voucher_code_platform": "Y123",
        #                 "purchase_order_number": "345345",
        #                 "sku": "BRSD#02",
        #                 "order_type": "Normal",
        #                 "invoice_number": "1342",
        #                 "cancel_return_initiator": "cancellation-customer",
        #                 "shop_sku": "BE494HLAAUE3SGAMZ-39898",
        #                 "is_reroute": "0",
        #                 "stage_pay_status": "unpaid",
        #                 "sku_id": "666",
        #                 "tracking_code_pre": "23534",
        #                 "order_item_id": "98108",
        #                 "shop_id": "dawen dp",
        #                 "order_flag": "GUATANTEE",
        #                 "is_fbl": "0",
        #                 "name": "Bean Rester Dooby Red",
        #                 "delivery_option_sof": "0",
        #                 "order_id": "31202",
        #                 "status": "canceled",
        #                 "product_main_image": "http://th-live-02.slatic.net/p/3/jianyue-7699-09550735-ccd244666871f12a523c77d68cd76d74-catalog.jpg",
        #                 "voucher_platform": "0.00",
        #                 "paid_price": "99.00",
        #                 "product_detail_url": "http://www.lazada.co.th/535590.html",
        #                 "warehouse_code": "WH-01",
        #                 "promised_shipping_time": "2014-10-15 19:12:15 +0800",
        #                 "shipping_type": "Dropshipping",
        #                 "created_at": "2014-10-15 19:12:15 +0800",
        #                 "voucher_seller_lpi": "0.00",
        #                 "shipping_fee_discount_platform": "0.00",
        #                 "wallet_credits": "0.00",
        #                 "updated_at": "2014-10-15 19:12:15 +0800",
        #                 "currency": "SGD",
        #                 "shipping_provider_type": "standard",
        #                 "voucher_platform_lpi": "0.00",
        #                 "shipping_fee_original": "0.00",
        #                 "item_price": "99.00",
        #                 "is_digital": "0",
        #                 "shipping_service_cost": "0",
        #                 "tracking_code": "456",
        #                 "shipping_fee_discount_seller": "0.00",
        #                 "shipping_amount": "0.00",
        #                 "reason_detail": "reason detail",
        #                 "return_status": "1",
        #                 "shipment_provider": "LEL",
        #                 "voucher_amount": "0.00",
        #                 "digital_delivery_info": "delivery",
        #                 "extra_attributes": "null"
        #             }, {
        #                 "pick_up_store_info": {
        #                     "pick_up_store_address": "Ali Center, Shenzhen",
        #                     "pick_up_store_name": "Alibaba",
        #                     "pick_up_store_open_hour": ["[\"Sunday 9:00-18:00\", \"Mondday,Tuesday,Wendnesday,Thursday,Friday 8:00-20:00\"]", "[\"Sunday 9:00-18:00\", \"Mondday,Tuesday,Wendnesday,Thursday,Friday 8:00-20:00\"]"],
        #                     "pick_up_store_code": "d4b04804-9192-4a8c-8ed1-5ebcd7d3c067"
        #                 },
        #                 "tax_amount": "6.48",
        #                 "reason": "reason",
        #                 "sla_time_stamp": "2019-06-24T23:59:59+08:00",
        #                 "voucher_seller": "0.00",
        #                 "purchase_order_id": "3454",
        #                 "voucher_code_seller": "X234",
        #                 "voucher_code": "X3453",
        #                 "package_id": "345",
        #                 "buyer_id": "1001",
        #                 "variation": "1",
        #                 "product_id": "12345",
        #                 "voucher_code_platform": "Y123",
        #                 "purchase_order_number": "345345",
        #                 "sku": "BRSD#02",
        #                 "order_type": "Normal",
        #                 "invoice_number": "1342",
        #                 "cancel_return_initiator": "cancellation-customer",
        #                 "shop_sku": "BE494HLAAUE3SGAMZ-39898",
        #                 "is_reroute": "0",
        #                 "stage_pay_status": "unpaid",
        #                 "sku_id": "666",
        #                 "tracking_code_pre": "23534",
        #                 "order_item_id": "98108",
        #                 "shop_id": "dawen dp",
        #                 "order_flag": "GUATANTEE",
        #                 "is_fbl": "0",
        #                 "name": "Bean Rester Dooby Red",
        #                 "delivery_option_sof": "0",
        #                 "order_id": "31202",
        #                 "status": "canceled",
        #                 "product_main_image": "http://th-live-02.slatic.net/p/3/jianyue-7699-09550735-ccd244666871f12a523c77d68cd76d74-catalog.jpg",
        #                 "voucher_platform": "0.00",
        #                 "paid_price": "99.00",
        #                 "product_detail_url": "http://www.lazada.co.th/535590.html",
        #                 "warehouse_code": "WH-01",
        #                 "promised_shipping_time": "2014-10-15 19:12:15 +0800",
        #                 "shipping_type": "Dropshipping",
        #                 "created_at": "2014-10-15 19:12:15 +0800",
        #                 "voucher_seller_lpi": "0.00",
        #                 "shipping_fee_discount_platform": "0.00",
        #                 "wallet_credits": "0.00",
        #                 "updated_at": "2014-10-15 19:12:15 +0800",
        #                 "currency": "SGD",
        #                 "shipping_provider_type": "standard",
        #                 "voucher_platform_lpi": "0.00",
        #                 "shipping_fee_original": "0.00",
        #                 "item_price": "99.00",
        #                 "is_digital": "0",
        #                 "shipping_service_cost": "0",
        #                 "tracking_code": "456",
        #                 "shipping_fee_discount_seller": "0.00",
        #                 "shipping_amount": "0.00",
        #                 "reason_detail": "reason detail",
        #                 "return_status": "1",
        #                 "shipment_provider": "LEL",
        #                 "voucher_amount": "0.00",
        #                 "digital_delivery_info": "delivery",
        #                 "extra_attributes": "null"
        #             }],
        #             "request_id": "0ba2887315178178017221014"
        #         }
        data = response.get('data')
        print(data)
        for datum in data:
            print(datum)
            for order_item in datum.get('order_items'):
                sku = order_item.get('sku')
                print(sku)
                lazada_item_id = order_item.get('order_item_id')
                print(lazada_item_id)
                product_id = self.env['product.product'].search([('default_code','=',sku)])
                if not product_id:
                    self.get_product_by_lazada_id(False,sku)
                    product_id = self.env['product.product'].search([('default_code','=',sku)])
                if product_id:
                    vals = {
                        'name': product_id.name,
                        'product_id': product_id.id,
                        'product_uom_qty': 1,
                        'lazada_order_line_id': order_item.get("order_item_id", False),
                        'price_unit': float(order_item.get("item_price", 0)),
                        'product_uom': product_id.uom_id.id,
                        'order_id': sale_order.id,
                        'tax_id': False
                    }
                    self.env['sale.order.line'].create(vals)








        # stop

    def get_orders_from_lazada_all(self,update_after, update_before, order_status):
        print("something")
        ts = int(round(time.time() * 1000))
        api_method = "/orders/get"
        parameters = {}
        parameters.update({'access_token': self.access_token})
        parameters.update({'app_key': self.app_key})
        parameters.update({'sign_method': 'sha256'})
        parameters.update({'timestamp': str(ts)})
        parameters.update({'status': order_status})
        if update_before:
            parameters.update({'update_before': update_before.replace(microsecond=0).isoformat()})
        if update_after:
            parameters.update({'update_after': update_after.replace(microsecond=0).isoformat()})
        print(parameters)
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.get(api_final_url)
        _logger.info(api_final_url)
        response = r.json()
        print(response)
        # response = {'data': {'count': 1, 'countTotal': 1, 'orders': [{'voucher_platform': 0.0, 'voucher': 0.0, 'warehouse_code': 'dropshipping', 'order_number': 560610362852235, 'voucher_seller': 0.0, 'created_at': '2022-11-02 11:28:42 +0800', 'voucher_code': '', 'gift_option': False, 'shipping_fee_discount_platform': 0.0, 'customer_last_name': '', 'promised_shipping_times': '', 'updated_at': '2022-11-02 11:28:54 +0800', 'price': '10.00', 'national_registration_number': '', 'shipping_fee_original': 38.0, 'payment_method': 'MIXEDCARD', 'customer_first_name': 'G********u', 'shipping_fee_discount_seller': 0.0, 'shipping_fee': 38.0, 'branch_number': '', 'tax_code': '', 'items_count': 1, 'delivery_info': '', 'statuses': ['pending'], 'address_billing': {'country': 'Philippines', 'address3': 'M**********************y', 'phone': '63*********96', 'address2': '', 'city': 'Quezon City', 'address1': 'S**************************e', 'post_code': '', 'phone2': '', 'last_name': '', 'address5': 'M*************************************************a', 'address4': 'Q*********y', 'first_name': 'Gracier Yu'}, 'extra_attributes': '', 'order_id': 560610362852235, 'remarks': '', 'gift_message': '', 'address_shipping': {'country': 'Philippines', 'address3': 'M**********************y', 'phone': '63*********96', 'address2': '', 'city': 'Quezon City', 'address1': 'S**************************e', 'post_code': '', 'phone2': '', 'last_name': '', 'address5': 'T**********a', 'address4': 'Q*********y', 'first_name': 'Gracier Yu'}}]}, 'code': '0', 'request_id': '2101596316679637728294048'}
        # print(response)
        if response.get('data'):
            data = response.get('data')
            orders = data.get('orders')
            for order in orders:
                order_id = order.get('order_id')
                self.get_order_details(order_id)
        else:
            raise ValidationError("Error in Lazada Sync")

        # stop










