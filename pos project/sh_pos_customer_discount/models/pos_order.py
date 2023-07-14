from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    """
        The following fields will contain the discount breakdown.
        Each field represents the type of discount as well as its
        discount percentage and amount.
        The computation and segregation of the discount type per orderline
        will be done in the models.js > export_as_JSON function.
        export_as_JSON will pass the values over to the backend side.
    """

    sc_discount = fields.Float(default=0)
    pwd_discount = fields.Float(default=0)
    # regular_discount = fields.Float(default=0)
    # pricelist_discount = fields.Float(default=0) not included since the computations is dynamic
    # promo_discount = fields.Float(default=0)
    # coupon_discount = fields.Float(default=0)

    sc_discount_amount = fields.Float(default=0)
    pwd_discount_amount = fields.Float(default=0)
    # regular_discount_amount = fields.Float(default=0)
    pricelist_discount_amount = fields.Float(default=0)
    # promo_discount_amount = fields.Float(default=0)
    # coupon_discount_amount = fields.Float(default=0)
