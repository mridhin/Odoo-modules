# -*- coding: utf-8 -*-

{
    'name': """POS Void - AWB""",
    'summary': '''void functions in pos''',
    'version': '15.0.1.0.1',
    'category': 'point of sale',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['point_of_sale'],

    'data': [
           'security/ir.model.access.csv',
           'data/sequence.xml',
           'views/pos_void.xml',
           'views/report.xml'
    ],
    'assets':{
            'point_of_sale.assets': [
             'awb_pos_void/static/src/js/pos_void.js',
             'awb_pos_void/static/src/xml/void.xml',
             ],
            'web.assets_qweb': [
            'awb_pos_void/static/src/xml/void.xml',
        ],
    },

    'application': True,
    'auto_install': False,
    'installable': True,
}
