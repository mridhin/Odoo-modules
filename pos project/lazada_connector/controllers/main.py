from odoo import http
from odoo.http import request, Response
import logging
import requests
import time
import werkzeug

logger = logging.getLogger(__name__)




class LazadaController(http.Controller):

    @http.route('/lazada_callbacks',  type='http', auth="public", website=True)
    def lazada_callbacks(self, **post):
        print(post)
        lazada_connector = request.env['lazada.connector'].sudo().search([], limit=1)
        if lazada_connector and post.get('code'):
            ts = int(round(time.time() * 1000))
            base_url = 'https://auth.lazada.com/rest'
            api_url = '/auth/token/create'
            final_url = base_url + api_url
            app_key = lazada_connector.app_key
            secret = lazada_connector.app_secret
            timestamp = str(ts)
            sign_method = 'sha256'
            code = post.get('code')
            data = {
               'app_key': app_key,
               'timestamp': timestamp,
               'sign_method': sign_method,
               'code': code,
            }
            sign = lazada_connector.sign(secret, api_url, data)
            data['sign'] = sign
            print(data)
            logger.info(data)
            response = requests.post(final_url, json=data)
            print(response)
            logger.info(response)
            json_response = response.json()
            logger.info(json_response)
            if not json_response.get('access_token'):
                return werkzeug.exceptions.Forbidden()
            access_token = json_response.get('access_token')
            refresh_token = json_response.get('refresh_token')
            lazada_connector.write({'access_token':access_token,'refresh_token':refresh_token,'state':'connection'})
            menu_id = request.env.ref('lazada_connector.menu_lazada_connector').id
            action_id = request.env.ref('lazada_connector.action_lazada_connector_form').id
            lazada_connector_id = lazada_connector.id
            redirect_url = "/web#id=" + str(lazada_connector_id) + "&cids=1&menu_id=" + str(menu_id) + "&action=" + str(
               action_id) + "&model=lazada.connector&view_type=form"
            print(redirect_url)
            return request.redirect(redirect_url)
        else:
            return werkzeug.exceptions.Forbidden()

    @http.route('/lazada_notifications', type='json', auth="public", website=True)
    def lazada_notifications(self):
        print(self)
        data = request.jsonrequest
        print(data)
        notification_type = data.get('message_type')
        print(notification_type)
        # data = {'seller_id': '9999', 'message_type': 0, 'data': {'order_status': 'This is a test message', 'trade_order_id': '567429568949464', 'status_update_time': 1668509543}, 'timestamp': 1668509543, 'site': 'lazada_sg'}
        lazada_connector = request.env['lazada.connector'].sudo().search([], limit=1)
        # return True
        if lazada_connector:
            # Receive from push mechonism or webhook
            # New product creation
            if notification_type in (3, 4, 5):
                lazada_connector.product_notification(data)
            # Sale order updates
            elif notification_type == 0:
                lazada_connector.get_orders_notification(data)
        return True


        # else:
        #     return werkzeug.exceptions.Forbidden()




