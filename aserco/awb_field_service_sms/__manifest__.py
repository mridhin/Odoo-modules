# -*- coding: utf-8 -*-
{
    'name': "AWB Field Service SMS",

    'summary': """AWB Field Service SMS""",

    'license': 'LGPL-3',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",
    'category': 'Services/Field Service',
    'version': '15.0.0.4',
    'depends': ['sms','project','industry_fsm', 'product', 'industry_fsm_sale_report', 'awb_l10n_ph_sms_smart_suite'],
    'data': [
        'security/ir.model.access.csv',
        'views/fsm_views.xml',
        'views/project_task.xml',
        'views/res_config_settings.xml'
    ],
    'images': ['static/description/icon.png'],
}