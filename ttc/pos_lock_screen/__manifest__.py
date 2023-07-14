# -*- coding: utf-8 -*-

{
    'name': 'POS Lock screen',
    'version': '15.0.1.0.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'POS Lock screen',
    'description': """
        POS Lock screen
""",
    'depends': ['base','point_of_sale', 'pos_hr'],
    'data': [
        'views/hr_employee_view.xml'
    ],
    'assets': {'point_of_sale.assets': ['pos_lock_screen/static/src/js/pos.js',
                                        'pos_lock_screen/static/src/js/pos_buttons.js',
                                        'pos_lock_screen/static/src/js/pos_buttons_lock.js',
                                        'pos_lock_screen/static/src/js/discount_popup.js',
                                        ],
               'web.assets_qweb': ['pos_lock_screen/static/src/xml/pos.xml',
                                   'pos_lock_screen/static/src/xml/pos_buttons.xml',
                                    'pos_lock_screen/static/src/xml/pos_buttons_lock.xml',
                                    'pos_lock_screen/static/src/xml/discount_popup.xml'
                                   ],},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': True,
}
