# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo.tools.safe_eval import datetime
from odoo.exceptions import UserError
from datetime import timedelta


class SelectProducts(models.TransientModel):
    _inherit = 'select.products'
    _rec_name = 'product_name'

    customer_type = fields.Selection(string="Customer Type",
                                     selection=[('RT', 'RT'), ('PV', 'PV'), ('EU', 'EU'), ('WS', 'WS'), ('MT', 'MT')])
    display_all_types = fields.Boolean('Display All Types')
    product_name = fields.Char(string="Products")
    product_line_ids = fields.One2many('select.products.line', 'select_id')
    location_id = fields.Many2one('stock.location')
    ws_col_selection = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('10', '10')],
        string='WS')
    rt_col_selection = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('10', '10')],
        string='RT')
    eu_col_selection = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('10', '10')],
        string='EU')
    pv_col_selection = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('10', '10')],
        string='PV')
    ws_count = fields.Integer()
    rt_count = fields.Integer()
    eu_count = fields.Integer()
    pv_count = fields.Integer()
    product_line = fields.Boolean()
    rt_lines = fields.Boolean()
    pv_lines = fields.Boolean()
    ws_lines = fields.Boolean()
    eu_lines = fields.Boolean()
    selected_warehouse = fields.Many2one('stock.location', string="Selected Warehouse", readonly=True)
    date_frame = fields.Selection(
        [('all_dates', 'All Dates'), ('current_month', 'Current Month'), ('last_10_days', 'Last 10 Days')],
        default='all_dates')
    sale_order_ids = fields.One2many('sale.order.wizard', 'select_product_id', string="Sale order Details")
    sale_order_month_ids = fields.One2many('sale.order.wizard', 'select_product_month_id', string="Sale order Details")
    sale_order_10_ids = fields.One2many('sale.order.wizard', 'select_product_10_id', string="Sale order Details")
    sale_order_journal_ids = fields.One2many('sale.order.journal.wizard', 'select_product_jou_id',
                                             string="Sale journal Details")
    sale_order_jou_month_ids = fields.One2many('sale.order.journal.wizard', 'select_product_month_jou_id',
                                               string="Sale journal Details")
    sale_order_jou_10_ids = fields.One2many('sale.order.journal.wizard', 'select_product_10_jou_id',
                                            string="Sale journal Details")
    purchase_order_ids = fields.One2many('purchase.order.wizard', 'select_purchase_id',
                                         string="Purchase Order Details")
    purchase_order_month_ids = fields.One2many('purchase.order.wizard', 'select_purchase_month_id',
                                               string="Purchase Order Details")
    purchase_order_10_ids = fields.One2many('purchase.order.wizard', 'select_purchase_10_id',
                                            string="Sale journal Details")
    purchase_jou_ids = fields.One2many('purchase.order.journal.wizard', 'select_purchase_jou_id',
                                       string="Purchase Order Details")
    purchase_jou_month_ids = fields.One2many('purchase.order.journal.wizard', 'select_purchase_month_jou_id',
                                             string="Purchase Order Details")
    purchase_jou_10_ids = fields.One2many('purchase.order.journal.wizard', 'select_purchase_10_jou_id',
                                          string="Purchase Order Details")
    credit_note_ids = fields.One2many('credit.note.wizard', 'select_credit_id',
                                      string="Credit Note Details")
    credit_note_month_ids = fields.One2many('credit.note.wizard', 'select_credit_month_id',
                                      string="Credit Note Details")
    credit_note_10_ids = fields.One2many('credit.note.wizard', 'select_credit_10_id',
                                      string="Credit Note Details")
    debit_note_ids = fields.One2many('debit.note.wizard', 'select_debit_id',
                                      string="debit Note Details")
    debit_note_10_ids = fields.One2many('debit.note.wizard', 'select_debit_10_id',
                                     string="debit Note Details")
    debit_note_month_ids = fields.One2many('debit.note.wizard', 'select_debit_month_id',
                                     string="debit Note Details")

    @api.onchange('display_all_types', 'ws_count', 'rt_count', 'eu_count', 'pv_count')
    def _onchange_display_all_types(self):
        print('--------==>>> self.rt_count', self.rt_count)
        if self.ws_count or self.rt_count or self.eu_count or self.pv_count:
            for line in self.product_line_ids.filtered(lambda line : line.is_selsected):
                line.update({
                    'is_default_rt' : False,
                    'is_default_ws' : False,
                    'is_default_eu' : False,
                    'is_default_pv' : False,
                })
    
    @api.onchange('date_frame')
    def _onchange_date_frame(self):
        for record in self:
            today = fields.Datetime.today()
            if record.sale_order_ids:
                if record.date_frame == "current_month":
                    list_ids = []
                    sale_jou_ids = []
                    pur_ids = []
                    pur_jor_ids = []
                    credit_ids = []
                    debit_ids = []
                    for rec in record.sale_order_ids:
                        date = rec.date_of_document
                        if today.month == date.month:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'sale_order_number': rec.sale_order_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            list_ids.append((0, 0, val))
                    for rec in record.purchase_order_ids:
                        date = rec.date_of_document
                        if today.month == date.month:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'purchase_order_number': rec.purchase_order_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            pur_ids.append((0, 0, val))
                    for rec in record.sale_order_journal_ids:
                        date = rec.date_of_document
                        if today.month == date.month:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'sale_Journal_number': rec.sale_Journal_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            sale_jou_ids.append((0, 0, val))
                    for rec in record.purchase_jou_ids:
                        date = rec.date_of_document
                        if today.month == date.month:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'purchase_journal_number': rec.purchase_journal_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            pur_jor_ids.append((0, 0, val))
                    for rec in record.debit_note_ids:
                        date = rec.date_of_document
                        if today.month == date.month:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'debit_memo_number': rec.debit_memo_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            debit_ids.append((0, 0, val))
                    for rec in record.credit_note_ids:
                        date = rec.date_of_document
                        if today.month == date.month:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'credit_memo_number': rec.credit_memo_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            credit_ids.append((0, 0, val))
                    record.update({'sale_order_month_ids': list_ids,
                                   'sale_order_jou_month_ids': sale_jou_ids,
                                   'purchase_order_month_ids': pur_ids,
                                   'purchase_jou_month_ids': pur_jor_ids,
                                   'credit_note_month_ids': credit_ids,
                                   'debit_note_month_ids': debit_ids})

                if record.date_frame == "last_10_days":
                    dateslist = [today - timedelta(days=day) for day in range(11)]
                    date_list = []
                    list_ids = []
                    list_ju_ids = []
                    pur_ids = []
                    pur_jur_ids = []
                    debit_ids = []
                    credit_ids = []
                    for da in dateslist:
                        date_list.append(da.date())
                    for rec in record.sale_order_ids:
                        if rec.date_of_document.date() in date_list:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'sale_order_number': rec.sale_order_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            list_ids.append((0, 0, val))
                    for rec in record.purchase_order_ids:
                        if rec.date_of_document.date() in date_list:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'purchase_order_number': rec.purchase_order_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            pur_ids.append((0, 0, val))
                    for rec in record.sale_order_journal_ids:
                        if rec.date_of_document.date() in date_list:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'sale_Journal_number': rec.sale_Journal_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            list_ju_ids.append((0, 0, val))
                    for rec in record.purchase_jou_ids:
                        if rec.date_of_document.date() in date_list:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'purchase_journal_number': rec.purchase_journal_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            pur_jur_ids.append((0, 0, val))
                    for rec in record.credit_note_ids:
                        if rec.date_of_document.date() in date_list:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'credit_memo_number': rec.credit_memo_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            credit_ids.append((0, 0, val))
                    for rec in record.debit_note_ids:
                        if rec.date_of_document.date() in date_list:
                            val = {
                                'date_of_document': rec.date_of_document,
                                'debit_memo_number': rec.debit_memo_number,
                                'customer_name': rec.customer_name,
                                'quantity': rec.quantity,
                                'uom_id': rec.uom_id,
                                'price': rec.price,
                                'discount': rec.discount,
                            }
                            debit_ids.append((0, 0, val))
                    record.update({'sale_order_10_ids': list_ids,
                                   'sale_order_jou_10_ids': list_ju_ids,
                                   'purchase_order_10_ids': pur_ids,
                                   'purchase_jou_10_ids': pur_jur_ids,
                                   'credit_note_10_ids': credit_ids,
                                   'debit_note_10_ids': debit_ids})

    @api.onchange('product_line_ids')
    def _compute_sale_order_ids(self):
        for rec in self:
            line_ids = rec.product_line_ids
            list = []
            jour_list = []
            pur_list = []
            pur_jor_list = []
            debit_list = []
            credit_list = []
            for line in line_ids:
                if line.is_selsected and line.line_check != True:
                    line.line_check = True
                    sale_order_line_id = self.env['sale.order.line'].search([('product_id', '=', line.product_id.id)])
                    for order_line in sale_order_line_id:
                        val = {
                            'date_of_document': order_line.order_id.date_order,
                            'sale_order_number': order_line.order_id.name,
                            'customer_name': order_line.order_id.partner_id.id,
                            'quantity': order_line.product_uom_qty,
                            'uom_id': order_line.product_uom.id,
                            'price': order_line.price_subtotal,
                            'discount': order_line.multiple_disc
                        }
                        list.append((0, 0, val))
                    purchase_order_line_id = self.env['purchase.order.line'].search(
                        [('product_id', '=', line.product_id.id)])
                    for pur_line in purchase_order_line_id:
                        val = {
                            'date_of_document': pur_line.order_id.date_order,
                            'purchase_order_number': pur_line.order_id.name,
                            'customer_name': pur_line.order_id.partner_id.id,
                            'quantity': pur_line.product_uom_qty,
                            'uom_id': pur_line.product_uom.id,
                            'price': pur_line.price_subtotal,
                            # 'discount': pur_line.multiple_disc
                        }
                        pur_list.append((0, 0, val))
                    sale_journal_line_id = self.env['account.move.line'].search(
                        [('product_id', '=', line.product_id.id)])
                    for journal_line in sale_journal_line_id:
                        if journal_line.move_id.journal_id.type == 'sale':
                            jour_val = {
                                'date_of_document': journal_line.move_id.invoice_date,
                                'sale_Journal_number': journal_line.move_id.name,
                                'customer_name': journal_line.move_id.partner_id.id,
                                'quantity': journal_line.quantity,
                                'uom_id': journal_line.product_uom_id.id,
                                'price': journal_line.price_subtotal,
                                'discount': journal_line.discount
                            }
                            jour_list.append((0, 0, jour_val))
                        if journal_line.move_id.journal_id.type == 'purchase':
                            jour_val = {
                                'date_of_document': journal_line.move_id.invoice_date,
                                'purchase_journal_number': journal_line.move_id.name,
                                'customer_name': journal_line.move_id.partner_id.id,
                                'quantity': journal_line.quantity,
                                'uom_id': journal_line.product_uom_id.id,
                                'price': journal_line.price_subtotal,
                                'discount': journal_line.discount
                            }
                            pur_jor_list.append((0, 0, jour_val))
                        if journal_line.move_id.move_type == 'out_refund':
                            cred_val = {
                                'date_of_document': journal_line.move_id.invoice_date,
                                'credit_memo_number': journal_line.move_id.name,
                                'customer_name': journal_line.move_id.partner_id.id,
                                'quantity': journal_line.quantity,
                                'uom_id': journal_line.product_uom_id.id,
                                'price': journal_line.price_subtotal,
                                'discount': journal_line.discount
                            }
                            credit_list.append((0, 0, cred_val))
                        if journal_line.move_id.move_type == 'in_refund':
                            debit_val = {
                                'date_of_document': journal_line.move_id.invoice_date,
                                'debit_memo_number': journal_line.move_id.name,
                                'customer_name': journal_line.move_id.partner_id.id,
                                'quantity': journal_line.quantity,
                                'uom_id': journal_line.product_uom_id.id,
                                'price': journal_line.price_subtotal,
                                'discount': journal_line.discount
                            }
                            debit_list.append((0, 0, debit_val))

            rec.update({'sale_order_ids': list,
                        'sale_order_journal_ids': jour_list,
                        'purchase_order_ids': pur_list,
                        'purchase_jou_ids': pur_jor_list,
                        'debit_note_ids':  debit_list,
                        'credit_note_ids': credit_list})

    @api.onchange('pv_col_selection')
    def onchange_pv_col_selection(self):
        for rec in self:
            rec.pv_count = int(rec.pv_col_selection)
            if rec.product_line_ids:
                line_ids = rec.product_line_ids
                product_id = line_ids.product_id.product_pvpricevarience_id
                for i in range(1, rec.pv_count + 1):
                    pv_price = 'pv_price_' + str(i)
                    pv_vol = 'pv_vol_' + str(i)
                    pv_disc = 'pv_disc_' + str(i)
                    line_ids[pv_price] = product_id[pv_price]
                    line_ids[pv_vol] = product_id[pv_vol]
                    line_ids[pv_disc] = product_id[pv_disc]

    @api.onchange('eu_col_selection')
    def onchange_eu_col_selection(self):
        for rec in self:
            rec.eu_count = int(rec.eu_col_selection)
            if rec.product_line_ids:
                line_ids = rec.product_line_ids
                product_id = line_ids.product_id.product_eupricevarience_id
                for i in range(1, rec.eu_count + 1):
                    eu_price = 'eu_price_' + str(i)
                    eu_vol = 'eu_vol_' + str(i)
                    eu_disc = 'eu_disc_' + str(i)
                    line_ids[eu_price] = product_id[eu_price]
                    line_ids[eu_vol] = product_id[eu_vol]
                    line_ids[eu_disc] = product_id[eu_disc]

    @api.onchange('rt_col_selection')
    def onchange_rt_col_selection(self):
        for rec in self:
            rec.rt_count = int(rec.rt_col_selection)
            if rec.product_line_ids:
                line_ids = rec.product_line_ids
                product_id = line_ids.product_id.product_rtpricevarience_id
                for i in range(1, rec.eu_count + 1):
                    rt_price = 'rt_price_' + str(i)
                    rt_vol = 'rt_vol_' + str(i)
                    rt_disc = 'rt_disc_' + str(i)
                    rt_vol_package = 'rt_vol_package_' + str(i)
                    rt_free_product = 'rt_free_product_' + str(i)
                    rt_free_product_qty = 'rt_free_product_qty_' + str(i)
                    rt_free_product_pkg = 'rt_free_product_pkg_' + str(i)
                    rt_com = 'rt_com_' + str(i)
                    line_ids[rt_price] = product_id[rt_price]
                    line_ids[rt_vol] = product_id[rt_vol]
                    line_ids[rt_disc] = product_id[rt_disc]
                    line_ids[rt_vol_package] = product_id[rt_vol_package]
                    line_ids[rt_free_product] = product_id[rt_free_product]
                    line_ids[rt_free_product_qty] = product_id[rt_free_product_qty]
                    line_ids[rt_free_product_pkg] = product_id[rt_free_product_pkg]
                    line_ids[rt_com] = product_id[rt_com]

    @api.onchange('ws_col_selection')
    def onchange_ws_col_selection(self):
        for rec in self:
            rec.ws_count = int(rec.ws_col_selection)
            if rec.product_line_ids:
                line_ids = rec.product_line_ids
                product_id = line_ids.product_id.product_wspricevarience_id
                for i in range(1, rec.ws_count + 1):
                    ws_price = 'ws_price_' + str(i)
                    ws_vol = 'ws_vol_' + str(i)
                    ws_disc = 'ws_disc_' + str(i)
                    ws_vol_package = 'ws_vol_package_' + str(i)
                    ws_free_product = 'ws_free_product_' + str(i)
                    ws_free_product_qty = 'ws_free_product_qty_' + str(i)
                    ws_free_product_pkg = 'ws_free_product_pkg_' + str(i)
                    ws_com = 'ws_com_' + str(i)
                    line_ids[ws_price] = product_id[ws_price]
                    line_ids[ws_vol] = product_id[ws_vol]
                    line_ids[ws_disc] = product_id[ws_disc]
                    line_ids[ws_vol_package] = product_id[ws_vol_package]
                    line_ids[ws_free_product] = product_id[ws_free_product]
                    line_ids[ws_free_product_qty] = product_id[ws_free_product_qty]
                    line_ids[ws_free_product_pkg] = product_id[ws_free_product_pkg]
                    line_ids[ws_com] = product_id[ws_com]

    @api.onchange('location_id')
    def onchange_location_id(self):
        for rec in self:
            if rec.product_line_ids:
                line_ids = rec.product_line_ids
                for line in line_ids:
                    if rec.location_id.id == 8:
                        location_ids = self.env['stock.location'].search([('location_id', '=', rec.location_id.id)])
                        loc_list = []
                        for location in location_ids:
                            loc_list.append(location.id)
                        quant_id = self.env['stock.quant'].search(
                            [('product_id', '=', line.product_id.id), ('location_id', 'in', loc_list)])
                        quant = 0.0
                        for quantity in quant_id:
                            quant += quantity.available_quantity

                        package_id = line.product_id.packaging_ids
                        val = {
                            'carton_packing': quant / float(
                                package_id.qty) if quant and package_id.qty else 0.0,
                            'inventory': quant,
                        }
                        line.update(val)
                    else:
                        quant_id = self.env['stock.quant'].search(
                            [('product_id', '=', line.product_id.id), ('location_id', '=', rec.location_id.id)])
                        package_id = line.product_id.packaging_ids
                        val = {
                            'carton_packing': float(quant_id.available_quantity) / float(
                                package_id.qty) if quant_id.available_quantity and package_id.qty else 0.0,
                            'inventory': quant_id.available_quantity,
                        }
                        line.update(val)
            rec.selected_warehouse = rec.location_id.id

    def search_products(self):
        for rec in self:
            if rec.product_name:
                if not rec.location_id:
                    raise UserError('Please select location.')
                list = []
                product_id = self.env['product.product'].search(
                    ['|', ('name', 'ilike', rec.product_name), ('default_code', 'ilike', rec.product_name)])
                if product_id:
                    rec.product_line = True
                    rec.rt_lines = True
                    for product_id in product_id:
                        package_id = product_id.packaging_ids
                        if rec.location_id.id == 8:
                            location_ids = self.env['stock.location'].search(
                                ['|', ('location_id', '=', rec.location_id.id), ('id', '=', 8)])
                            loc_list = []
                            for location in location_ids:
                                loc_list.append(location.id)
                            quant_id = self.env['stock.quant'].search(
                                [('product_id', '=', product_id.id), ('location_id', 'in', loc_list)])
                            quant = 0.0
                            for quantity in quant_id:
                                quant = quant + float(quantity.available_quantity)
                            if quant != 0 and package_id.qty != 0:
                                carton_packing = quant / float(package_id.qty)
                            else:
                                carton_packing = 0
                            inventory = quant
                        else:
                            quant_id = self.env['stock.quant'].search(
                                [('product_id', '=', product_id.id), ('location_id', '=', rec.location_id.id)])
                            carton_packing = float(quant_id.available_quantity) / float(
                                package_id.qty) if quant_id.available_quantity and package_id.qty else 0.0
                            inventory = quant_id.available_quantity
                        val = {
                            'product_id': product_id.id,
                            'carton_packing': float(carton_packing),
                            'packing': package_id.name,
                            'inventory': inventory,
                            'reserve': product_id.reverse,
                            'eu_date': product_id.product_eupricevarience_id.date,
                            'eu_price': product_id.product_eupricevarience_id.price,
                            'eu_disc': product_id.product_eupricevarience_id.discount,
                            'rt_date': product_id.product_rtpricevarience_id.date,
                            'rt_price': product_id.product_rtpricevarience_id.price,
                            'rt_disc': product_id.product_rtpricevarience_id.discount,
                            'rt_comm': product_id.product_rtpricevarience_id.commission,
                            'ws_date': product_id.product_wspricevarience_id.date,
                            'ws_price': product_id.product_wspricevarience_id.price,
                            'ws_disc': product_id.product_wspricevarience_id.discount,
                            'ws_comm': product_id.product_wspricevarience_id.commission,
                            'pv_date': product_id.product_pvpricevarience_id.date,
                            'pv_price': product_id.product_pvpricevarience_id.price,
                            'pv_disc': product_id.product_pvpricevarience_id.discount,
                            'pv_comm': product_id.product_pvpricevarience_id.commission,
                        }
                        list.append((0, 0, val))
                    rec.update({'product_line_ids': list})
                    rec.selected_warehouse = rec.location_id.id

    
    def create_products_lines(self):
        line_list = []
        order_id = self.env['sale.order'].browse(self._context.get('active_id', False))
        ws_price = ""
        eu_price = ""
        rt_price = ""
        pv_price = ""
        pv_vol = ""
        rt_vol = ""
        ws_vol = ""
        eu_vol = ""
        for line in self.product_line_ids.filtered(lambda line : line.is_selsected):
            print('--------==>>> line', line)
            print('--------==>>> line.is_default_rt', line.is_default_rt)
            print('--------==>>> line.is_default_ws', line.is_default_ws)
            print('--------==>>> line.is_default_eu', line.is_default_eu)
            print('--------==>>> line.is_default_pv', line.is_default_pv)
            is_pv = False
            is_ws = False
            is_rt = False
            is_eu = False
            if line.is_default_pv:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'order_id': order_id.id,
                    'display_type': False,
                    'price_unit': float(line.pv_price) if line.pv_price else 0.0,
                    'product_uom_qty': 1.0,
                    'discount' : float(line.pv_disc) if line.pv_disc else 0.0,
                    'product_warehouse_id': self.location_id.warehouse_id.id
                }
                line_list.append((0, 0, line_vals))
                continue
            else:
                for i in range(1, self.pv_count + 1):
                    pv_sel = 'pv_sel_' + str(i)
                    if line[pv_sel] == True:
                        is_pv = True
                        pv_price = 'pv_price_' + str(i)
                        pv_vol = 'pv_vol_' + str(i)
                        pv_disc = 'pv_disc_' + str(i)
                        pv_price = line[pv_price]
                        pv_vol = line[pv_vol]
                        pv_disc = line[pv_disc]

                        line_vals = {
                            'product_id': line.product_id.id,
                            'product_uom': line.product_id.uom_id.id,
                            'order_id': order_id.id,
                            'display_type': False,
                            'price_unit': float(pv_price) if pv_price else 0.0,
                            'product_uom_qty': float(pv_vol) if pv_vol else 0.0,
                            'discount' : float(pv_disc) if pv_disc else 0.0,
                            'product_warehouse_id': self.location_id.warehouse_id.id
                        }
                        line_list.append((0, 0, line_vals))
                        continue
                if is_pv:
                    continue
            if line.is_default_ws:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'order_id': order_id.id,
                    'display_type': False,
                    'price_unit': float(line.ws_price) if line.ws_price else 0.0,
                    'product_uom_qty': 1.0,
                    'discount' : float(line.ws_disc) if line.ws_disc else 0.0,
                    'product_warehouse_id': self.location_id.warehouse_id.id
                }
                line_list.append((0, 0, line_vals))
                continue
            else:
                for i in range(1, self.ws_count + 1):
                    ws_sel = 'ws_sel_' + str(i)
                    if line[ws_sel] == True:
                        is_ws = True
                        ws_price = 'ws_price_' + str(i)
                        ws_vol = 'ws_vol_' + str(i)
                        ws_disc = 'ws_disc_' + str(i)
                        ws_vol_package = 'ws_vol_package_' + str(i)
                        ws_free_product = 'ws_free_product_' + str(i)
                        ws_free_product_qty = 'ws_free_product_qty_' + str(i)
                        ws_free_product_pkg = 'ws_free_product_pkg_' + str(i)
                        ws_com = 'ws_com_' + str(i)
                        ws_price = line[ws_price]
                        ws_vol = line[ws_vol]
                        ws_disc = line[ws_disc]
                        ws_vol_package = line[ws_vol_package]
                        ws_free_product = line[ws_free_product]
                        ws_free_product_qty = line[ws_free_product_qty]
                        ws_free_product_pkg = line[ws_free_product_pkg]
                        ws_com = line[ws_com]
                        print(ws_free_product)
                        line_vals = {
                            'product_id': ws_free_product.id,
                            'product_uom': ws_free_product.uom_id.id,
                            'price_unit': 0,
                            'display_type': False,
                            'order_id': order_id.id,
                            'product_packaging_qty': float(ws_vol_package),
                            'product_packaging_id': ws_free_product_pkg and ws_free_product_pkg.id or False,
                            'product_uom_qty': float(ws_free_product_qty),
                            'product_warehouse_id': self.location_id.warehouse_id.id
                        }
                        line_list.append((0, 0, line_vals))
                        continue
                if is_ws:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'display_type': False,
                        'order_id': order_id.id,
                        'price_unit': float(ws_price) if ws_price else 0.0,
                        'product_uom_qty': float(ws_vol) if ws_vol else 0.0,
                        'product_warehouse_id': self.location_id.warehouse_id.id
                    }
                    line_list.append((0, 0, line_vals))
                    continue
            if line.is_default_eu:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'order_id': order_id.id,
                    'display_type': False,
                    'price_unit': float(line.eu_price) if line.eu_price else 0.0,
                    'product_uom_qty': 1.0,
                    'discount' : float(line.eu_disc) if line.eu_disc else 0.0,
                    'product_warehouse_id': self.location_id.warehouse_id.id
                }
                line_list.append((0, 0, line_vals))
                continue
            else:
                for i in range(1, self.eu_count + 1):
                    eu_sel = 'eu_sel_' + str(i)
                    if line[eu_sel] == True:
                        is_eu = True
                        eu_price = 'eu_price_' + str(i)
                        eu_vol = 'eu_vol_' + str(i)
                        eu_disc = 'eu_disc_' + str(i)
                        eu_price = line[eu_price]
                        eu_vol = line[eu_vol]
                        eu_disc = line[eu_disc]
                
                        line_vals = {
                            'product_id': line.product_id.id,
                            'product_uom': line.product_id.uom_id.id,
                            'order_id': order_id.id,
                            'display_type': False,
                            'price_unit': float(eu_price) if eu_price else 0.0,
                            'product_uom_qty': float(eu_vol) if eu_vol else 0.0,
                            'discount' : float(eu_disc) if eu_disc else 0.0,
                            'product_warehouse_id': self.location_id.warehouse_id.id
                        }
                        line_list.append((0, 0, line_vals))
                        continue
                if is_eu:
                    continue
            if line.is_default_rt:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'order_id': order_id.id,
                    'display_type': False,
                    'price_unit': float(line.rt_price) if line.rt_price else 0.0,
                    'product_uom_qty': 1.0,
                    'discount' : float(line.rt_disc) if line.rt_disc else 0.0,
                    'product_warehouse_id': self.location_id.warehouse_id.id
                }
                print('--------==>>> line_vals', line_vals)
                line_list.append((0, 0, line_vals))
                continue
            else:
                for i in range(1, self.rt_count + 1):
                    rt_sel = 'rt_sel_' + str(i)
                    if line[rt_sel] == True:
                        is_rt = True
                        rt_price = 'rt_price_' + str(i)
                        rt_vol = 'rt_vol_' + str(i)
                        rt_disc = 'rt_disc_' + str(i)
                        rt_vol_package = 'rt_vol_package_' + str(i)
                        rt_free_product = 'rt_free_product_' + str(i)
                        rt_free_product_qty = 'rt_free_product_qty_' + str(i)
                        rt_free_product_pkg = 'rt_free_product_pkg_' + str(i)
                        rt_com = 'rt_com_' + str(i)
                        rt_price = line[rt_price]
                        rt_vol = line[rt_vol]
                        rt_disc = line[rt_disc]
                        rt_vol_package = line[rt_vol_package]
                        rt_free_product = line[rt_free_product]
                        rt_free_product_qty = line[rt_free_product_qty]
                        rt_free_product_pkg = line[rt_free_product_pkg]
                        rt_com = line[rt_com]
                        line_vals = {
                            'product_id': rt_free_product.id,
                            'product_uom': rt_free_product.uom_id.id,
                            'price_unit': 0,
                            'order_id': order_id.id,
                            'display_type': False,
                            'product_uom_qty': float(rt_free_product_qty),
                            'product_packaging_qty': float(rt_vol_package),
                            'product_packaging_id': rt_free_product_pkg and rt_free_product_pkg.id or False,
                            'product_warehouse_id': self.location_id.warehouse_id.id
                        }
                        line_list.append((0, 0, line_vals))
                        continue
                if is_rt:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'order_id': order_id.id,
                        'price_unit': float(rt_price) if rt_price else 0.0,
                        'product_uom_qty': float(rt_vol) if rt_vol else 0.0,
                        'product_warehouse_id': self.location_id.warehouse_id.id,
                        'discount' : rt_disc,
                        'display_type': False,
                    }
                    line_list.append((0, 0, line_vals))
                    continue
        print('--------==>>> line_list', line_list)
        order_id.write({
            'order_line' : line_list
        })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref(
                'sale.view_order_form').id,
            'res_id': order_id.id,
            'target': 'current'
        }

        # sol._onchange_discount()
        # sol._onchange_suggest_packaging()
        # sol._onchange_update_product_packaging_qty()
        # sol.onchange_product_warehouse_id()
    
    def select_products(self):
        for rec in self:
            print('--------==>>> rec', rec)
            if self.flag_order == 'so':
                data = rec.create_products_lines()
            else:
                data = rec.po_create_products_lines()
            return data
    
    def po_create_products_lines(self):
        line_list = []
        order_id = self.env['purchase.order'].browse(self._context.get('active_id', False))
        ws_price = ""
        eu_price = ""
        rt_price = ""
        pv_price = ""
        pv_vol = ""
        rt_vol = ""
        ws_vol = ""
        eu_vol = ""
        for line in self.product_line_ids.filtered(lambda line : line.is_selsected):
            print('--------==>>> line', line)
            is_pv = False
            is_ws = False
            is_rt = False
            is_eu = False
            for i in range(1, self.pv_count + 1):
                pv_sel = 'pv_sel_' + str(i)
                if line[pv_sel] == True:
                    is_pv = True
                    pv_price = 'pv_price_' + str(i)
                    pv_vol = 'pv_vol_' + str(i)
                    pv_disc = 'pv_disc_' + str(i)
                    pv_price = line[pv_price]
                    pv_vol = line[pv_vol]
                    pv_disc = line[pv_disc]

                    line_vals = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'order_id': order_id.id,
                        'display_type': False,
                        'price_unit': float(pv_price) if pv_price else 0.0,
                        'product_qty': float(pv_vol) if pv_vol else 0.0,
                        'discount' : float(pv_disc) if pv_disc else 0.0,
                        'date_planned': order_id.date_planned or datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'product_warehouse_id': self.location_id.warehouse_id.id
                    }
                    line_list.append((0, 0, line_vals))
                    continue
            if is_pv:
                continue
            for i in range(1, self.ws_count + 1):
                ws_sel = 'ws_sel_' + str(i)
                if line[ws_sel] == True:
                    is_ws = True
                    ws_price = 'ws_price_' + str(i)
                    ws_vol = 'ws_vol_' + str(i)
                    ws_disc = 'ws_disc_' + str(i)
                    ws_vol_package = 'ws_vol_package_' + str(i)
                    ws_free_product = 'ws_free_product_' + str(i)
                    ws_free_product_qty = 'ws_free_product_qty_' + str(i)
                    ws_free_product_pkg = 'ws_free_product_pkg_' + str(i)
                    ws_com = 'ws_com_' + str(i)
                    ws_price = line[ws_price]
                    ws_vol = line[ws_vol]
                    ws_disc = line[ws_disc]
                    ws_vol_package = line[ws_vol_package]
                    ws_free_product = line[ws_free_product]
                    ws_free_product_qty = line[ws_free_product_qty]
                    ws_free_product_pkg = line[ws_free_product_pkg]
                    ws_com = line[ws_com]
                    print(ws_free_product)
                    line_vals = {
                        'product_id': ws_free_product.id,
                        'product_uom': ws_free_product.uom_id.id,
                        'price_unit': 0,
                        'display_type': False,
                        'order_id': order_id.id,
                        'product_qty': float(ws_free_product_qty),
                        'date_planned': order_id.date_planned or datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'product_warehouse_id': self.location_id.warehouse_id.id
                    }
                    line_list.append((0, 0, line_vals))
                    continue
            if is_ws:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'display_type': False,
                    'order_id': order_id.id,
                    'price_unit': float(ws_price) if ws_price else 0.0,
                    'product_qty': float(ws_vol) if ws_vol else 0.0,
                    'date_planned': order_id.date_planned or datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT),
                    # 'product_warehouse_id': self.location_id.warehouse_id.id
                }
                line_list.append((0, 0, line_vals))
                continue
            for i in range(1, self.eu_count + 1):
                eu_sel = 'eu_sel_' + str(i)
                if line[eu_sel] == True:
                    is_eu = True
                    eu_price = 'eu_price_' + str(i)
                    eu_vol = 'eu_vol_' + str(i)
                    eu_disc = 'eu_disc_' + str(i)
                    eu_price = line[eu_price]
                    eu_vol = line[eu_vol]
                    eu_disc = line[eu_disc]
            
                    line_vals = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'order_id': order_id.id,
                        'display_type': False,
                        'price_unit': float(eu_price) if eu_price else 0.0,
                        'product_qty': float(eu_vol) if eu_vol else 0.0,
                        'discount' : float(eu_disc) if eu_disc else 0.0,
                        'date_planned': order_id.date_planned or datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'product_warehouse_id': self.location_id.warehouse_id.id
                    }
                    line_list.append((0, 0, line_vals))
                    continue
            if is_eu:
                continue
            for i in range(1, self.eu_count + 1):
                rt_sel = 'rt_sel_' + str(i)
                if line[rt_sel] == True:
                    is_rt = True
                    rt_price = 'rt_price_' + str(i)
                    rt_vol = 'rt_vol_' + str(i)
                    rt_disc = 'rt_disc_' + str(i)
                    rt_vol_package = 'rt_vol_package_' + str(i)
                    rt_free_product = 'rt_free_product_' + str(i)
                    rt_free_product_qty = 'rt_free_product_qty_' + str(i)
                    rt_free_product_pkg = 'rt_free_product_pkg_' + str(i)
                    rt_com = 'rt_com_' + str(i)
                    rt_price = line[rt_price]
                    rt_vol = line[rt_vol]
                    rt_disc = line[rt_disc]
                    rt_vol_package = line[rt_vol_package]
                    rt_free_product = line[rt_free_product]
                    rt_free_product_qty = line[rt_free_product_qty]
                    rt_free_product_pkg = line[rt_free_product_pkg]
                    rt_com = line[rt_com]
                    line_vals = {
                        'product_id': rt_free_product.id,
                        'product_uom': rt_free_product.uom_id.id,
                        'price_unit': 0,
                        'order_id': order_id.id,
                        'display_type': False,
                        'product_qty': float(rt_free_product_qty),
                        'date_planned': order_id.date_planned or datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'product_warehouse_id': self.location_id.warehouse_id.id
                    }
                    line_list.append((0, 0, line_vals))
                    continue
            if is_rt:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'order_id': order_id.id,
                    'price_unit': float(rt_price) if rt_price else 0.0,
                    'product_qty': float(rt_vol) if rt_vol else 0.0,
                    # 'product_warehouse_id': self.location_id.warehouse_id.id,
                    'discount' : rt_disc,
                    'display_type': False,
                    'date_planned': order_id.date_planned or datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT),
                }
                line_list.append((0, 0, line_vals))
                continue
        print('--------==>>> line_list', line_list)
        order_id.write({
            'order_line' : line_list
        })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': self.env.ref(
                'purchase.purchase_order_form').id,
            'res_id': order_id.id,
            'target': 'current'
        }