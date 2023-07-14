# -*- coding: utf-8 -*-
{
    'name': "X-Reading Module- AWB",

    'summary': "X-Reading Module Inherited",

    'description': """
        Adds X-Reading to POS App
    """,

    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '15.0.1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'point_of_sale',
        'cc_x_reading'
    ],
    # always loaded
    'data': [
       'views/x_reading_report_inherit.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
          
        ],
        'web.assets_qweb': [
          
        ]
    }
}

