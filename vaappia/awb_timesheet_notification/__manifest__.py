# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'AWB Via Appia Scheduler Customization',
    'summary': "AWB Via Appia Scheduler Customization",
    'version': '1.0.0',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/",
    'description': """
 """,
    'category': 'Customization',
    'depends': ['base','hr_timesheet'],
    'data': [
        
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    
    'data': [
        "security/ir.model.access.csv",
        'data/scheduler_cron_data.xml',
        'views/res_config_settings_views.xml',
    ],
 
}
