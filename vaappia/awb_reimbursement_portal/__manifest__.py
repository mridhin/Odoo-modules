# -*- coding: utf-8 -*-

{
    'name': """AWB Reimbursement Portal""",
    'summary': '''AWB Reimbursement Portal User''',
    'version': '15.0.1.0.4',
    'category': 'Website',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['base','account','website','portal'],

    'data': [
        'views/employee_portal_user.xml',
    ],
    'assets':{
            'web.assets_frontend': [
                'awb_reimbursement_portal/static/src/css/portal_design.css',
                'awb_reimbursement_portal/static/src/js/employee_portal_user.js',
                ],
    },
    'application': True,
    'auto_install': False,
    'installable': True,
}

