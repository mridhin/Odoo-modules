# -*- coding: utf-8 -*-

{
	"name" : "All pos orders list in Odoo ",
	"version" : "15.0.0.3",
	"category" : "Point of Sale",
	"depends" : ['awb_l10n_ph_pos'],
	
	'summary': 'Apps manage point of sale orders from the POS screen pos all order list pos order list pos list point of sales list Pos All Orders List on POS screen pos orderlist pos all orderlist list pos list orders pos all orders display pos orders list pos all orders',

	"description": """

	""",
	
	"author": "Achieve Without Borders, Inc.",
    "website": "https://www.achievewithoutborders.com/page/odoo",
	"data": [
		'views/custom_pos_view.xml',
	],

	'assets': {
        'point_of_sale.assets': [
            'pos_orders_list/static/src/css/pos.css',
            'pos_orders_list/static/src/js/models.js',
            'pos_orders_list/static/src/js/jquery-barcode.js',
            'pos_orders_list/static/src/js/Popups/PosOrdersDetail.js',
			'pos_orders_list/static/src/js/Screens/controlbutton.js',
			'pos_orders_list/static/src/js/Screens/POSOrdersScreen.js',
			'pos_orders_list/static/src/js/Screens/POSOrders.js',
			'pos_orders_list/static/src/js/Screens/ClientListScreen.js',
			'pos_orders_list/static/src/js/Screens/ReceiptScreen.js',
        ],
        'web.assets_qweb': [
            'pos_orders_list/static/src/xml/**/*',
        ],
    },

	"auto_install": False,
	"installable": True,

}
