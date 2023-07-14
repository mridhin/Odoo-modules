# -*- coding: utf-8 -*-
{
    'name': "AWB Proxy Booker Customer Portal",
    'version': '15.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'AWB Proxy Booker Customer Portal',
    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders',
    "license": "LGPL-3",
    'description': """
    Display the Sales Order record in Customer Portal 
    when the partner booker name is tagged in Sales Order form.
    """,
    'depends': ['sale'],
    'data': [
        'views/sale_portal_templates.xml'
    ],
    'assets': {
    },
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
