# -*- coding: utf-8 -*-
{
    'name': "Hotel_Management",

    'summary': """
        Module for hotel rooms booking ,bill payment and report reation""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ridhin",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/booking.xml',
        'views/room.xml',
        'views/orderfood.xml',
        'reprot/report.xml',

    ],

}