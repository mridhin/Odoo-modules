# -*- coding: utf-8 -*-
{
    "name": "AWB Philippine Point of Sale Localization",
    "summary": "AWB Philippine Point of Sale Localization",
    "description": """
        AWB Philippine Point of Sale Localization
    """,
    "author": "Achieve Without Borders, Inc.",
    "website": "https://www.achievewithoutborders.com/page/odoo",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Localization",
    "version": "15.0.7.3",
    # any module necessary for this one to work correctly
    "depends": [
        "point_of_sale",
        "crm",
        "sale_management",
        "pos_sale_receipt",
        "sh_pos_customer_discount",
        "awb_pos_sc_pwdID",
        "awb_common",
    ],
    # always loaded
    'data': [
        'views/res_company.xml',
        "views/pos_session.xml",
        'views/crm_team_views.xml',
        'views/pos_order_view.xml',
        'views/pos_terminal_views.xml',

    ],
    "assets": {
        "web.assets_qweb": [
            "awb_l10n_ph_pos/static/src/xml/pos_receipt.xml",
            "awb_l10n_ph_pos/static/src/xml/Screens/ProductScreen/ActionpadWidget.xml",
        ],
        # point_of_sale.assets added
        "point_of_sale.assets": [
            "awb_l10n_ph_pos/static/src/js/pos_receipt.js",
            "awb_l10n_ph_pos/static/src/js/models.js",
            "awb_l10n_ph_pos/static/src/js/Screens/ReceiptScreen/OrderReceipt.js",
            "awb_l10n_ph_pos/static/src/js/Screens/PaymentScreen/PaymentScreen.js",
            "awb_l10n_ph_pos/static/src/css/pos_receipts.css",
            "awb_l10n_ph_pos/static/src/js/Screens/ProductScreen/ControlButtons/ActionpadWidget.js",
            "awb_l10n_ph_pos/static/src/js/Screens/ProductScreen/ControlButtons/OrderWidget.js",
            "awb_l10n_ph_pos/static/src/js/Screens/TicketScreen/TicketScreen.js"
        ],
    },
}
