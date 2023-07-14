
from odoo import models, fields

class SelectSaleOrder(models.TransientModel):
    _name = 'sale.order.wizard'

    date_of_document = fields.Datetime(string="Date of Document")
    sale_order_number = fields.Char(string="Sales Order Number")
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price = fields.Float(string="Price")
    discount = fields.Char(string="Discount")
    select_product_id = fields.Many2one('select.products')
    select_product_month_id = fields.Many2one('select.products')
    select_product_10_id = fields.Many2one('select.products')

class SelectSaleOrderJournal(models.TransientModel):
    _name = 'sale.order.journal.wizard'

    date_of_document = fields.Datetime(string="Date of Document")
    sale_Journal_number = fields.Char(string="Sales Journal Number")
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price = fields.Float(string="Price")
    discount = fields.Char(string="Discount")
    select_product_jou_id = fields.Many2one('select.products')
    select_product_month_jou_id = fields.Many2one('select.products')
    select_product_10_jou_id = fields.Many2one('select.products')

class SelectCreditNote(models.TransientModel):
    _name = 'credit.note.wizard'

    date_of_document = fields.Datetime(string="Date of Document")
    credit_memo_number = fields.Char(string="Credit Memo Number")
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price = fields.Float(string="Price")
    discount = fields.Char(string="Discount")
    select_credit_id = fields.Many2one('select.products')
    select_credit_month_id = fields.Many2one('select.products')
    select_credit_10_id = fields.Many2one('select.products')

