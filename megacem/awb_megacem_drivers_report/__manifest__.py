# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Drivers Report Custom",
    'summary': """
        
        """,
    'description': """
        
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Report',
    'version': '4.0.1',
    'depends': ['base', 'mail', 'hr', 'report_xlsx', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/driver_report_group.xml',
        'data/journal_data.xml',
        'views/drivers_report_views.xml',
        'views/stages_views.xml',
        'views/destinations_views.xml',
        'views/bulk_number_views.xml',
        'views/th_number_views.xml',
        'views/type_of_operation_views.xml',
        'views/type_of_delivery_views.xml',
        'views/drivers_report_menus.xml',
        'views/drivers_seq.xml',
        'views/assets_view.xml',
        'views/res_partner.xml',
        'views/ir_server_action.xml',
        'views/account_move_views.xml',

        'reports/report_drivers_report.xml',
        'reports/report_format.xml',
        'reports/report_actions.xml',
        'reports/report.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
