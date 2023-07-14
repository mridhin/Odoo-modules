# -*- coding: utf-8 -*-

{
    'name': 'POS SC/PWD ID odoo15',
    'version': '15.0.1',
    'category': 'POS',
    'sequence': 356,
    'summary': 'POS SC/PWD ID ',
    'description': """POS SC/PWD ID """,

    'author': 'AWB',
    'website': '',

    'depends': ['point_of_sale', 'sh_pos_customer_discount'],
    'data': [
            'views/partner_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            #TODO: remove unused assets
            # 'awb_pos_sc_pwdID/static/src/js/scpwdPopup.js',
            # 'awb_pos_sc_pwdID/static/src/js/ProductScreen.js',
            'awb_pos_sc_pwdID/static/src/js/models.js',

            # new assets
            'awb_pos_sc_pwdID/static/src/js/ClientDetailsEdit.js',
        ],
        'web.assets_qweb': [
            # 'awb_pos_sc_pwdID/static/src/xml/ProductScreen/scpwdPopup.xml',
            # 'awb_pos_sc_pwdID/static/src/xml/OrderReceipt.xml',

            # new assets
            'awb_pos_sc_pwdID/static/src/xml/Screens/ClientDetailsEdit.xml',
        ],
    },
    
    'application': True,
    'license': 'LGPL-3'
}
