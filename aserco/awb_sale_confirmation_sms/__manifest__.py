# -*- coding: utf-8 -*-
{
    'name': "AWB Sale Confirmation SMS",

    'summary': """Customized Confirmation SMS""",

    'license': 'LGPL-3',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",
    'category': 'Services/Field Service',
    'version': '15.0.0.2',
    'depends': ['sale', 'sms','industry_fsm'],
    'data': [
        'views/res_config_settings.xml',
    ],

    'images': ['static/description/icon.png'],
}
