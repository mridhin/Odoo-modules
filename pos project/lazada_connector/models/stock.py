from odoo import fields, models, api, _
import requests
import time
import logging
from lxml import etree
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
  _inherit = "stock.move.line"

  def _action_done(self):
      res = super(StockMoveLine, self)._action_done()
      for rec in self:
          if rec.product_id.is_lazada_product and (rec.location_dest_id.id == rec.product_id.lazada_shop_id.warehouse_id.lot_stock_id.id or rec.location_id.id == rec.product_id.lazada_shop_id.warehouse_id.lot_stock_id.id):
              rec.product_id.lazada_shop_id.product_stock_update(rec.product_id)
      return res


class LazadaConnectorProduct(models.Model):
    _inherit = 'lazada.connector'

    def product_stock_update(self, product_id):
        product_qty = product_id.qty_available
        ts = int(round(time.time() * 1000))
        root = etree.Element("Request")
        product_element = etree.SubElement(root,'Product')
        skus_element = etree.SubElement(product_element,'Skus')
        irq = etree.SubElement(skus_element,"Sku")
        seller_sku= etree.SubElement(irq,'SellerSku')
        seller_sku.text = str(product_id.default_code)
        mrt = etree.SubElement(irq,'Quantity')
        mrt.text = str(int(product_qty))
        xml_request = etree.tostring(root,encoding='UTF-8')
        api_method = "/product/price_quantity/update"
        parameters = {}
        parameters.update({'access_token':self.access_token})
        parameters.update({'app_key':self.app_key})
        parameters.update({'sign_method':'sha256'})
        parameters.update({'timestamp':str(ts)})
        parameters.update({'payload':xml_request.decode('utf-8')})
        print(parameters)
        sign = self.sign(self.app_secret, api_method, parameters)
        api_final_url = self.api_final_url(api_method, parameters, sign)
        r = requests.post(api_final_url, data = parameters)
        response = r.json()
        print(response)
        if response.get('message'):
            raise UserError(_(response.get('detail',"Error in stock update")))
