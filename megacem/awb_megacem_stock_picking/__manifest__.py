# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB - Megacem Stock Picking Custom",
    'summary': """
        
        """,
    'description': """
        
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Custom',
    'version': '1.0.',
    'depends': ['base', 'awb_megacem_drivers_report', 'stock'],
    'data': [
        'views/stock_picking_form_inherit_view.xml',
        'views/th_number_form_inherit_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
