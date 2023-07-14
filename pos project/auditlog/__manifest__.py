# -*- coding: utf-8 -*-
{
    "name": "AWB User Recent Logs",
    'summary': '''AWB User Recent Logs''',
    "version": "15.0.1.0.0",
    'description': """
        It will show the recent activity of users""",
    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    "category": "Tools",
    "depends": ["base","account"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/auditlog_view.xml",
        "views/http_session_view.xml",
        "views/http_request_view.xml",
    ],
    'assets':{
        'web.assets_backend': {
            '/auditlog/static/src/js/log_print.js',
            
        },
        'web.assets_qweb': {
            
        },
    },
    "application": True,
    "installable": True,
    'auto_install': False,
}
