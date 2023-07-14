# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Contacts Form",
    'summary': """
        AWB Contacts Form
        """,
    'description': """
        AWB Contacts Form
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': "contacts",
    'version': '15.0.1.0.0',
    'depends': ['base','account','contacts'],
    'data': [
            'security/ir.model.access.csv',
            'views/res_partner.xml',
            'views/delivery_area_menu.xml',
            
            
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
