# -*- coding: utf-8 -*-

{
    'name': """ AWB Sale Reserve Level """,
    'summary': '''AWB Sale Reserve Level''',
    'version': '15.0.1.0.1',
    'category': 'Accounting',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['sale_management',],

    'data': [
           'views/inherit_product.template.xml',
    ],
    'assets':{
             
    },
    
    'application': True,
    'auto_install': False,
    'installable': True,
}
