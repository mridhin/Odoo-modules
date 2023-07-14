# -*- coding: utf-8 -*-
{
    'name': "Reset Counter Module",

    'summary': "Adds a reset counter to the sequence module.",

    'description': """
        Adds a reset counter to the sequence module.
    """,

    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],
    # always loaded
    'data': [
       'views/ir_sequence_views.xml',
    ],

}

