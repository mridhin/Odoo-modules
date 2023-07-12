{
    "name": "AWB Current User Edit Option Accessbility",
    "summary": "To Restrict User to edit it's Own Record",
    "version": "15.0.1.0.0",
    "category": "Web",
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    "depends": [
        "web",
    ],
    "assets": {
        "web.assets_backend": [
            "awb_restrict_curr_user_edit/static/src/js/form_controller.js",
        ]
    },
    "installable": True,
    "excludes": [
        "web_access_rule_buttons",
    ],
}
