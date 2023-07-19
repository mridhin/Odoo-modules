# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB 9-Box Appraisal",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/appraisal_period.xml',
        'views/employee.xml',
        'views/employee_list.xml'
    ],
    'qweb': ["static/src/xml/appraisal_period_tem.xml"],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
