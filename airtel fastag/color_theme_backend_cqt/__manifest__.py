# -*- coding: utf-8 -*-
{
    'name': "Change Color Theme, Theme Color Change",
    'version': '13.0.1.0.0',
    'sequence': 1,
    'website': "https://cronquotech.odoo.com",
    'summary': '''Color change theme,
     theme, theme color, Dynamic theme Color,
      theme change,
       multi, multi color,
        multi color theme,
         them multi color, change color, ''',
    'description': "Using this module user able to set color in theme per user",
    'author': 'CRON QUOTECH',
    'category': 'Theme',
    'depends': ['base', 'web'],
    'data': [
        'views/templates.xml',
        'views/res_users_view.xml',
    ],
    'images': [
        'static/description/banner.png','static/description/cronquotech_banner_screenshot.png'
    ],
    'qweb': [
    ],
    "support": "cronquotech@gmail.com",
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    'auto_install': False
}
