from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.template'

    carton_packing = fields.Char(string="Carton Packing")
    price_change_date = fields.Datetime(string="Price Change Date")
    promo_price_per_volume = fields.Float(string="Promo Price per volume per type")
    max_level_discount = fields.Float(string="Max Level Discount per type")
    cash_on_delivery_discount = fields.Float(string="Cash on Delivery Discount")
    cod_disc_1 = fields.Float(string="COD disc 1")
    cod_disc_2 = fields.Float(string="COD disc 2")
    cod_disc_3 = fields.Float(string="COD disc 3")
    cod_disc_4 = fields.Float(string="COD disc 4")
    commission = fields.Char(string="Commission")
    inventory = fields.Char(string="Inventory")
    product_wspricevarience_id = fields.One2many('product.wspricevarience', 'product_wspriceid')
    product_eupricevarience_id = fields.One2many('product.eupricevarience', 'product_eupriceid')
    product_pvpricevarience_id = fields.One2many('product.pvpricevarience', 'product_pvpriceid')
    product_rtpricevarience_id = fields.One2many('product.rtpricevarience', 'product_rtpriceid')
    reverse = fields.Char()