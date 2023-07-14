# -*- coding: utf-8 -*-
{
    'name': "AWB Product Inquiry Custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Achieve Without Borders",
    "website": '"http://www.achievewithoutborders.com"',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fl_so_po_multi_products'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/select_product_wizard_view.xml',
        'views/sale_order.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'awb_product_inquiry_order_line/static/src/css/style.css',
        ]
    }
}
