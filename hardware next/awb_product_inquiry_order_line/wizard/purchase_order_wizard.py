
from odoo import models, fields

class SelectPurchaseOrder(models.TransientModel):
    _name = 'purchase.order.wizard'

    date_of_document = fields.Datetime(string="Date of Document")
    purchase_order_number = fields.Char(string="Purchase Order Number")
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price = fields.Float(string="Price")
    discount = fields.Char(string="Discount")
    select_purchase_id = fields.Many2one('select.products')
    select_purchase_month_id = fields.Many2one('select.products')
    select_purchase_10_id = fields.Many2one('select.products')

class SelectPurchaseOrderJournal(models.TransientModel):
    _name = 'purchase.order.journal.wizard'

    date_of_document = fields.Datetime(string="Date of Document")
    purchase_journal_number = fields.Char(string="Purchase Journal Number")
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price = fields.Float(string="Price")
    discount = fields.Char(string="Discount")
    select_purchase_jou_id = fields.Many2one('select.products')
    select_purchase_month_jou_id = fields.Many2one('select.products')
    select_purchase_10_jou_id = fields.Many2one('select.products')

class SelectDebitNote(models.TransientModel):
    _name = 'debit.note.wizard'

    date_of_document = fields.Datetime(string="Date of Document")
    debit_memo_number = fields.Char(string="Debit Memo Number")
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price = fields.Float(string="Price")
    discount = fields.Char(string="Discount")
    select_debit_id = fields.Many2one('select.products')
    select_debit_month_id = fields.Many2one('select.products')
    select_debit_10_id = fields.Many2one('select.products')