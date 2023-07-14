from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    """
        The following fields will contain the VAT related information per orderline.
        The computation and segregation of the VAT related info
        will be done in the models.js
        export_as_JSON will pass the values over to the backend side.
    """

    vatable_sales = fields.Float(default=0)
    vat_amount = fields.Float(default=0)
    zero_rated_sales = fields.Float(default=0)
    vat_exempt_sales = fields.Float(default=0)
    # Check order line vat exclusive
    is_vat_exclusive = fields.Boolean(string='isVatExclusive')
    
