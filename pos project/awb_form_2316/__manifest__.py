# -*- coding: utf-8 -*-

{
    'name': """ AWB Compensation Form""",
    'summary': '''BIR Form 2316 for Financial Reporting - Certificate of Compensation Payment/Tax Withheld''',
    'version': '15.0.1.0.1',
    'category': 'Accounting',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['base', 'website','stock','product','website_sale','account'],

    'data': [
           'security/ir.model.access.csv',
           'views/form_compensation.xml',
           'views/template.xml',
    ],
    'assets':{
             
    },
    'currency': 'EUR',
    'application': True,
    'auto_install': False,
    'installable': True,
}
