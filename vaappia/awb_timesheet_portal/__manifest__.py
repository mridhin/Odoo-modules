# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': 'AWB Timesheet Portal',
    'version': '15.0.1.0.5',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/",
    'description': """ Description Text """,
    'category': 'Timesheet',
    'depends': ['base', 'hr_timesheet', 'timesheet_grid','sale_timesheet'],
    'license': 'LGPL-3',
    'data': [
        'views/templates.xml',
        'views/hr_timesheet.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'awb_timesheet_portal/static/css/timesheet_dialog_design.css',
            'awb_timesheet_portal/static/js/timesheet_popup.js',
            'awb_timesheet_portal/static/js/export_timesheet.js',
            'awb_timesheet_portal/static/js/xlsx.full.min.js']
    },

    'installable': True,
    'application': False,
    'auto_install': False
}
