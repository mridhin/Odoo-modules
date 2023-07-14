# -*- coding: utf-8 -*-
{
    'name': "Gitlab Connector",
    'version': '15.0.1.1.1',
    'summary': """Gitlab Connector""",
    'description': """
    """,
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': '',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/gitlab_cron.xml',
        'views/gitlab_connector_view.xml',
        'views/project_view.xml',
        'views/resource_allocation_report_view.xml',
        'views/res_users_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'LGPL-3',
}
