# -*- coding: utf-8 -*-


{
    "name": "Point Of Sale Solo Parent Discount",
    "author": "AWB",
    "category": "Point of Sale",
    "license": "OPL-1",
    "summary": "POS Solo Parent Discount, Point Of Sale Solo Parent Discount, Point Of Sale Order Line Customer Discount, POS Custom Discount,Point Of Sale Discount,POS Discount, POS Line Discount,Special Customer Discount Odoo",
    "description": """Do you want to add a discount automatically from a customer in the point of sale order? This module helps to apply POS order discount automatically when selecting the customer, so you need to define it only once time then after, it will automatically be added in every order.""",
    "version": "15.0.0.1",
    "depends": ["point_of_sale", "sh_pos_customer_discount", "awb_l10n_ph_pos"],
    "application": True,
    "data": [
        'views/pos_order_view.xml',
    ],
    'assets': {
        #point_of_sale.assets added
        'point_of_sale.assets': [
            'sh_pos_solo_parent_discount/static/src/js/pos_buttons_sp.js',
            'sh_pos_solo_parent_discount/static/src/js/discount_popup.js',
            'sh_pos_solo_parent_discount/static/src/js/models.js'
        ],
        'web.assets_qweb': [
            'sh_pos_solo_parent_discount/static/src/xml/discount_popup_sp.xml',
            'sh_pos_solo_parent_discount/static/src/xml/pos_buttons_sp.xml',
            'sh_pos_solo_parent_discount/static/src/xml/pos_receipt_view.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    "price": 000,
    "currency": "EUR"
}
