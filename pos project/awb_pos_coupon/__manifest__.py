{
    "name": "Pos coupon",
    "version": "15.0.1.0.0",
    "category": "Product",
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    "license": "AGPL-3",
    "depends": ["pos_coupon"],
    'assets': {
        'point_of_sale.assets': [
            'awb_pos_coupon/static/src/js/coupon.js',
        ],
    },
    "installable": True,
    "auto_install": False,
}