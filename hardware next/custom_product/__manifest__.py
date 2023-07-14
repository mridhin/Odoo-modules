# -*- coding: utf-8 -*-
{
    'name': "Custom Purchase",
    'summary': "",
    'description': """""",
    'category': 'POS',
    'version': '1.0',
    'depends': ['base', 'product', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_supplierinfo_views.xml',
    ],
    'demo': [
        
    ],
    'installable': True,
    'license': 'LGPL-3',
}