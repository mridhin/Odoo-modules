# -*- coding: utf-8 -*-

{
    "name" : "POS Orders Reprint in Odoo",
    "version" : "15.0.0.1",
    "category" : "Point of Sale",
    "depends" : ['pos_orders_list'],
    
    'summary': 'Apps pos reprint pos repeat pos reprint pos order receipt reprint from pos order receipt reprint point of sale reprint point of sale repeat point of sale reprint point of sale receipt reprint from point of sale order receipt reprint point of sales receipt',
    "description": """
    """,
    "author": "Achieve Without Borders, Inc.",
    "website": "https://www.achievewithoutborders.com/page/odoo",
  
    'assets': {
        'point_of_sale.assets': [
            "pos_orders_reprint/static/src/js/Screens/POSOrdersScreen.js",
            "pos_orders_reprint/static/src/js/Screens/OrderReprintScreen.js",
            "pos_orders_reprint/static/src/js/Screens/OrderReprintReceipt.js",
        ],
        'web.assets_qweb': [
            'pos_orders_reprint/static/src/xml/**/*',
        ],
    },
    

    "auto_install": False,
    "installable": True,

}
