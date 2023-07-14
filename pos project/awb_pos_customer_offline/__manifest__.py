# -*- coding: utf-8 -*-

{
    'name': """POS Customer Offline""",
    'summary': '''Creating customer offline in pos''',
    'version': '15.0.1.0.1',
    'category': 'Point of Sale',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['base', 'point_of_sale'],

    'data': [
             'views/pos_config.xml', 
    ],
    'assets':{
            'point_of_sale.assets': [
                'awb_pos_customer_offline/static/src/js/awb_models.js',
                'awb_pos_customer_offline/static/src/js/awbClientListScreen.js',
                ],
            
    },
    

    
    
    'currency': 'EUR',

    'application': True,
    'auto_install': False,
    'installable': True,
}
