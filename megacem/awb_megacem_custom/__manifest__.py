# -*- coding: utf-8 -*-
{
    'name': "AWB Megacem Customization",

    'summary': "AWB Megacem Customization",

    'description': "AWB Megacem Customization",

    'author': "Achieve Without Borders, Inc",
    'website': "https://www.achievewithoutborders.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '14.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition', 'stock'],

    # always loaded
    'data': [
        'views/purchase_requisition.xml',
        'views/stock_views.xml',

    ],
}