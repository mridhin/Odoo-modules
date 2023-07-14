# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Aserco Website Form",
    "summary": """
        Developed Features:
	Dynamic values from backend for Service Needed field
	Dynamic values from backend for Area field with domain filter set based on selected Service Needed
	Dynamic values from backend for Preferred Service Date field with domain filter set based on selected Service Needed, Area, Timeslot & Available Allocation in the object Allocated Technician Schedule lines
	Also ensure to show only upcoming 30 days in asc order for Preferred Service Date field
	Store selected dynamic values in crm.lead object
	Store loggedin user's partner id value in backend field (partner_id) in crm.lead object
        
        """,
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "",
    "website": "",
    "depends": ["web"],
    "data": [
        'views/template.xml',
    ],
    "assets": {
        "web.assets_backend": [
        ],
        "web.assets_frontend": [
            "/aserco_website_form/static/src/js/appointment.js",
        ],
    },
    "installable": True,
}
