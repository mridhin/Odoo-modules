# -*- coding: utf-8 -*-

{
    'name': """POS Return Product - AWB""",
    'summary': '''Return Product functions in pos''',
    'version': '15.0.1.0.1',
    'category': 'point of sale',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['point_of_sale'],

    'data': [
          
    ],
    'assets':{
            'point_of_sale.assets': [
             'awb_return_products/static/src/xml/refund_hide.xml',
             ],
            'web.assets_qweb': [
            'awb_return_products/static/src/xml/refund_hide.xml',
        ],
    },

    'application': True,
    'auto_install': False,
    'installable': True,
}
